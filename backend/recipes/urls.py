from django.urls import path

from .views import (
    RecipeViewSet, IngredientListView,
    IngredientRetrieveView, RecipeShortLinkView,
    ShoppingCartView, DownloadShoppingCartView, FavoriteView
)


urlpatterns = [
    path('recipes/',
         RecipeViewSet.as_view({'get': 'list', 'post': 'create'}),
         name='recipe-list'),
    path('recipes/<int:pk>/',
         RecipeViewSet.as_view(
             {'get': 'retrieve',
              'patch': 'partial_update',
              'delete': 'destroy'}),
         name='recipe-detail'),
    path('recipes/<int:pk>/get-link/',
         RecipeShortLinkView.as_view(),
         name='recipe-get-link'),
    path('recipes/<int:pk>/shopping_cart/',
         ShoppingCartView.as_view(), name='shopping-cart'),
    path('recipes/<int:pk>/favorite/', FavoriteView.as_view(),
         name='favorite'),
    path('recipes/download_shopping_cart/',
         DownloadShoppingCartView.as_view(), name='download-shopping-cart'),
    path('ingredients/',
         IngredientListView.as_view(), name='ingredients-list'),
    path('ingredients/<int:pk>/',
         IngredientRetrieveView.as_view(), name='ingredients-retrieve')
]
