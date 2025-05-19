from django.contrib import admin
from django.urls import path, include
from recipes.views import RecipeShortLinkRedirectView

urlpatterns = [
    path('admin/', admin.site.urls),

    path('api/users/', include('users.urls')),
    path('api/', include('recipes.urls')),
    path('s/<str:short_code>/', RecipeShortLinkRedirectView.as_view(),
         name='recipe-short-redirect'),

    path('api/', include('djoser.urls')),
    path('api/auth/', include('djoser.urls.authtoken')),
]
