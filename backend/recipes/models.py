from django.db import models
from django.core.validators import MinValueValidator
from django.conf import settings


class Ingredient(models.Model):
    name = models.CharField(
        max_length=128, null=False, blank=False, name='name'
    )
    measurement_unit = models.CharField(
        max_length=64, null=False, blank=False, name='measurement_unit'
    )


class Recipe(models.Model):
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='author'
    )
    image = models.ImageField(
        upload_to='recipes/', blank=False,
        null=False, name='image'
    )
    name = models.CharField(
        max_length=256, null=False, blank=False, name='name'
    )
    text = models.TextField(null=False, blank=False, name='text')
    cooking_time = models.IntegerField(
        blank=False, null=False, name='cooking_time',
        validators=[MinValueValidator(1)]
    )

    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
    )


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, blank=False, null=False
    )
    ingredient = models.ForeignKey(
        Ingredient, on_delete=models.CASCADE, blank=False,
        null=False
    )
    amount = models.IntegerField(
        validators=[MinValueValidator(1)], blank=False,
        null=False, name='amount'
    )

    class Meta:
        unique_together = ('recipe', 'ingredient')


class ShoppingCart(models.Model):
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE,
        blank=False, null=False
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        blank=False, null=False
    )


class Favorite(models.Model):
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE,
        blank=False, null=False
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        blank=False, null=False
    )
