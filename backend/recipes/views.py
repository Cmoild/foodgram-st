from rest_framework import viewsets, generics, permissions, views, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from rest_framework.exceptions import NotFound
from django.shortcuts import redirect
from django.http import HttpResponse

from .models import (
    Recipe, Ingredient, ShoppingCart, RecipeIngredient, Favorite
)
from .serializers import (
    IngredientSerializer, RecipeListSerializer, RecipeCreateUpdateSerializer,
    RecipeShortSerializer
)
from .permissions import IsAuthorOrReadOnly


class StandardPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'limit'


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    pagination_class = StandardPagination
    permission_classes = [IsAuthorOrReadOnly]

    def get_queryset(self):
        queryset = super().get_queryset()
        request = self.request
        user = request.user
        params = request.query_params

        if author_id := params.get('author'):
            queryset = queryset.filter(author_id=author_id)

        if params.get('is_favorited') == '1' and user.is_authenticated:
            queryset = queryset.filter(favorite__author=user).distinct()

        if params.get('is_in_shopping_cart') == '1' and user.is_authenticated:
            queryset = queryset.filter(shoppingcart__author=user).distinct()

        return queryset

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return RecipeCreateUpdateSerializer
        return RecipeListSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'request': self.request})
        return context


class RecipeShortLinkView(generics.RetrieveAPIView):
    queryset = Recipe.objects.all()
    permission_classes = [permissions.AllowAny]

    def retrieve(self, request, *args, **kwargs):
        recipe = self.get_object()
        short_code = hex(recipe.id)[2:]
        short_url = request.build_absolute_uri(f'/s/{short_code}/')
        return Response({
            "short-link": short_url
        })


class RecipeShortLinkRedirectView(views.APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, short_code):
        try:
            recipe_id = int(short_code, 16)
            return redirect(f'/recipes/{recipe_id}')
        except NotFound:
            raise NotFound('Not found')


class IngredientListView(generics.ListAPIView):
    serializer_class = IngredientSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        queryset = Ingredient.objects.all()
        name = self.request.query_params.get('name')

        if name:
            queryset = queryset.filter(name__startswith=name)

        return queryset


class IngredientRetrieveView(generics.RetrieveAPIView):
    serializer_class = IngredientSerializer
    permission_classes = [permissions.AllowAny]
    queryset = Ingredient.objects.all()


class ShoppingCartView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        recipe = get_object_or_404(Recipe, pk=pk)

        if (ShoppingCart.objects.filter(author=request.user,
                                        recipe=recipe).exists()):
            return Response(
                {"errors": 'Recipe is already in shopping cart'},
                status=status.HTTP_400_BAD_REQUEST
            )

        ShoppingCart.objects.create(author=request.user, recipe=recipe)
        serializer = RecipeShortSerializer(
            recipe,
            context={'request': request}
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, pk):
        recipe = get_object_or_404(Recipe, pk=pk)
        cart_item = ShoppingCart.objects.filter(
            author=request.user,
            recipe=recipe
        ).first()

        if not cart_item:
            return Response(
                {"errors": 'Recipe does not exist in shopping cart'},
                status=status.HTTP_400_BAD_REQUEST
            )

        cart_item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class DownloadShoppingCartView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        shopping_cart = ShoppingCart.objects.filter(author=request.user)
        data = {}
        for item in shopping_cart:
            ingredient_amount = RecipeIngredient.objects.filter(
                recipe=item.recipe)
            for obj in ingredient_amount:
                mu = obj.ingredient.measurement_unit
                name = f'{obj.ingredient.name} ({mu})'
                if name not in data.keys():
                    data[name] = obj.amount
                else:
                    data[name] += obj.amount
        output = '\n'.join([f'* {n} - {data[n]}' for n in data.keys()])
        return HttpResponse(output, content_type='text/plain', status=200)


class FavoriteView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        recipe = get_object_or_404(Recipe, pk=pk)

        if Favorite.objects.filter(author=request.user,
                                   recipe=recipe).exists():
            return Response(
                {"errors": "Рецепт уже в списке покупок"},
                status=status.HTTP_400_BAD_REQUEST
            )

        Favorite.objects.create(author=request.user, recipe=recipe)
        serializer = RecipeShortSerializer(
            recipe,
            context={'request': request}
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, pk):
        recipe = get_object_or_404(Recipe, pk=pk)
        cart_item = Favorite.objects.filter(
            author=request.user,
            recipe=recipe
        ).first()

        if not cart_item:
            return Response(
                {"errors": "Рецепта нет в списке покупок"},
                status=status.HTTP_400_BAD_REQUEST
            )

        cart_item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
