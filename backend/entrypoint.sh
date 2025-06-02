#!/bin/sh

# Ингредиенты заргужаются в БД после применения миграций
# Это происходит по сигналу post_migrate
# Код для загрузки находится в recipes_models/apps.py
# Данные загружаются только в том случае, если таблица пуста
python manage.py migrate
python manage.py collectstatic --noinput
gunicorn --bind 0.0.0.0:8000 backend.wsgi
