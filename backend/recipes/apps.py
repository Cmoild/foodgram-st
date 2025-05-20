from django.apps import AppConfig
import json


class RecipesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'recipes'

    def ready(self):
        from django.db.models.signals import post_migrate
        post_migrate.connect(load_initial_data, sender=self)


def load_initial_data(sender, **kwargs):
    if kwargs['app_config'].name == 'recipes':
        Ingredient = sender.get_model('Ingredient')
        if not Ingredient.objects.exists():
            with open('./ingredients.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                for item in data:
                    Ingredient.objects.get_or_create(**item)
