from django.core.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework import status


def tags_validator(tags, Tag):
    if not tags:
        raise ValidationError('Добавьте теги')
    valid_tags = Tag.objects.filter(id__in=tags)
    if len(valid_tags) != len(tags):
        return Response('Страница не найдена',
                        status=status.HTTP_404_NOT_FOUND)
    return valid_tags


def ingredients_validator(ingredients, Ingredient):
    valid_ingredients = {}
    for ingredient in ingredients:
        valid_ingredients[ingredient["id"]] = int(ingredient["amount"])
    if not ingredients:
        raise ValidationError('Добавьте ингредиенты')
    inrgedient_list = [
        item['id'] for item in ingredients
    ]
    if len(inrgedient_list) != len(set(inrgedient_list)):
        raise ValidationError('Ингредиенты должны быть уникальными')
    valid_ingredients_in_db = Ingredient.objects.filter(
        pk__in=inrgedient_list)
    if len(valid_ingredients_in_db) != len(inrgedient_list):
        return Response('Страница не найдена',
                        status=status.HTTP_404_NOT_FOUND)
    for ingredient in valid_ingredients_in_db:
        valid_ingredients[ingredient.pk] = (ingredient,
                                            valid_ingredients[ingredient.pk])
    return valid_ingredients
