from django.core.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework import status


def tags_validator(tags, Tag):
    for tag in tags:
        if not Tag.objects.filter(id=tag.id).exists():
            return Response('Страница не найдена',
                            status=status.HTTP_404_NOT_FOUND)


def ingredients_validator(ingredients, Ingredient):
    valid_ingredients = {}
    for ingredient in ingredients:
        valid_ingredients[ingredient['ingredient']] = int(ingredient['amount'])
    if not ingredients:
        raise ValidationError('Добавьте ингредиенты')
    inrgedient_list = [
        item['ingredient'] for item in ingredients
    ]
    if len(inrgedient_list) != len(set(inrgedient_list)):
        raise ValidationError('Ингредиенты должны быть уникальными')
    for ingredient in inrgedient_list:
        if not Ingredient.objects.filter(id=ingredient.id).exists():
            return Response('Страница не найдена',
                            status=status.HTTP_404_NOT_FOUND)
