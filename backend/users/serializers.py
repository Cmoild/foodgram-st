from rest_framework import serializers
from users_models.models import CustomUser, Subscription
from recipes_models.models import Recipe


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ('id', 'email', 'username', 'first_name',
                  'last_name', 'password')
        extra_kwargs = {
            'email': {'required': True},
            'username': {'required': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
            'password': {'required': True},
        }

    def create(self, validated_data):
        user = CustomUser.objects.create_user(**validated_data)
        return user


class AvatarUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('avatar',)


class UserListSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()
    avatar = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = (
            'id', 'email', 'username', 'first_name',
            'last_name', 'is_subscribed', 'avatar'
        )

    def get_is_subscribed(self, obj):
        request = self.context['request']
        user = request.user

        if user.is_authenticated:
            return user.follower.filter(author=obj).exists()
        return False

    def get_avatar(self, obj):
        request = self.context['request']
        if obj.avatar and hasattr(obj.avatar, 'url'):
            return request.build_absolute_uri(obj.avatar.url)
        return None


class RecipeShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscriptionUserSerializer(UserListSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta(UserListSerializer.Meta):
        fields = UserListSerializer.Meta.fields + ('recipes', 'recipes_count')

    def get_recipes(self, obj):
        request = self.context['request']
        recipes_limit = request.query_params.get('recipes_limit')

        recipes_qs = obj.author.all()
        if recipes_limit is not None:
            try:
                limit = int(recipes_limit)
                recipes_qs = recipes_qs[:limit]
            except ValueError:
                pass

        return RecipeShortSerializer(recipes_qs,
                                     many=True, context=self.context).data

    def get_recipes_count(self, obj):
        return obj.author.count()


class SubscriptionCreateSerializer(serializers.ModelSerializer):
    author = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.all()
    )

    class Meta:
        model = Subscription
        fields = ('author',)

    def validate_author(self, value):
        user = self.context['request'].user

        if value == user:
            raise serializers.ValidationError(
                'You cannot subscribe to yourself.'
            )

        if user.follower.filter(author=value).exists():
            raise serializers.ValidationError(
                'You are already subscribed to this user.'
            )

        return value

    def create(self, validated_data):
        user = self.context['request'].user
        author = validated_data['author']
        return Subscription.objects.create(user=user, author=author)
