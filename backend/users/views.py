from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.core.files.base import ContentFile
from rest_framework.pagination import PageNumberPagination

import base64
import uuid

from .models import CustomUser, Subscription
from .serializers import (
    UserListSerializer,
    UserCreateSerializer,
    SubscriptionUserSerializer,
)


class StandardPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'limit'


class UserListCreateView(generics.ListCreateAPIView):
    queryset = CustomUser.objects.all()
    permission_classes = [permissions.AllowAny]
    pagination_class = StandardPagination

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return UserCreateSerializer
        return UserListSerializer


class UserDetailView(generics.RetrieveAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserListSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'id'


class CurrentUserView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = UserListSerializer(
            request.user, context={'request': request})
        return Response(serializer.data)


class AvatarUploadView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def put(self, request):
        avatar_base64 = request.data.get('avatar')

        if not avatar_base64:
            return Response({'avatar': ['This field is required']}, status=400)

        try:
            format, imgstr = avatar_base64.split(';base64,')
            ext = format.split('/')[-1]
            file_name = f'{uuid.uuid4()}.{ext}'
            data = ContentFile(base64.b64decode(imgstr), name=file_name)
        except Exception:
            return Response({'avatar': ['Invalid image format']}, status=400)

        user = request.user
        user.avatar = data
        user.save()

        return Response(
            {'avatar': request.build_absolute_uri(user.avatar.url)})

    def delete(self, request):
        user = request.user
        user.avatar.delete(save=True)
        return Response(status=status.HTTP_204_NO_CONTENT)


class SubscriptionsView(generics.ListAPIView):
    serializer_class = SubscriptionUserSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardPagination

    def get_queryset(self):
        return CustomUser.objects.filter(following__user=self.request.user)


class SubscribeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, id):
        author = get_object_or_404(CustomUser, id=id)
        user = request.user

        if author == user:
            return Response(
                {'detail': 'You cannot subscribe to yourself'}, status=400)

        if Subscription.objects.filter(user=user, author=author).exists():
            return Response(
                {'detail': 'You are already subscribed to this user'},
                status=400)

        Subscription.objects.create(user=user, author=author)
        serializer = SubscriptionUserSerializer(author,
                                                context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, id):
        author = get_object_or_404(CustomUser, id=id)
        user = request.user
        subscription = Subscription.objects.filter(user=user, author=author)

        if subscription.exists():
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(
            {'detail': 'You are not subscribed to this user'}, status=400)
