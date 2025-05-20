from django.contrib import admin
from .models import (Ingredient, Recipe,
                     RecipeIngredient, ShoppingCart, Favorite)


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'favorites_count')
    search_fields = ('name', 'author__email', 'author__username')
    inlines = [RecipeIngredientInline]

    def favorites_count(self, obj):
        return obj.favorite_set.count()
    favorites_count.short_description = 'В избранном'


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    search_fields = ('name',)


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'ingredient', 'amount')


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('author', 'recipe')


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('author', 'recipe')
