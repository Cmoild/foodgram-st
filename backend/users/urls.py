from django.urls import path
from .views import (
    UserDetailView, CurrentUserView, AvatarUploadView,
    SubscriptionsView, SubscribeView, UserListCreateView
)

urlpatterns = [
    path('', UserListCreateView.as_view(), name='user-list-create'),
    path('<int:id>/', UserDetailView.as_view(), name='user-detail'),
    path('me/', CurrentUserView.as_view(), name='user-me'),
    path('me/avatar/', AvatarUploadView.as_view(), name='user-avatar'),

    # Подписки
    path('subscriptions/', SubscriptionsView.as_view(), name='subscriptions'),
    path('<int:id>/subscribe/', SubscribeView.as_view(), name='subscribe'),
]
