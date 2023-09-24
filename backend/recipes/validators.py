from django.core.exceptions import ValidationError


def tags_validator(tags, Tag):
    if not tags:
        raise ValidationError()
    valid_tags = Tag.objects.filter(id__in=tags)
    if len(valid_tags) != len(tags):
        raise ValidationError()
    return valid_tags


def ingredients_validator(ingredients, Ingredient):
    valid_ingredients = {}
    for ingredient in ingredients:
        valid_ingredients[ingredient["id"]] = int(ingredient["amount"])
    if not ingredients:
        raise ValidationError()
    inrgedient_list = [
        item['id'] for item in ingredients
    ]
    unique_ingredient_list = set(inrgedient_list)
    if len(inrgedient_list) != len(unique_ingredient_list):
        raise ValidationError('Ингредиенты должны быть уникальными')
    valid_ingredients_in_db = Ingredient.objects.filter(
        pk__in=unique_ingredient_list)
    if not valid_ingredients_in_db:
        raise ValidationError('Ингредиенты неправильные')
    for ingredient in valid_ingredients_in_db:
        valid_ingredients[ingredient.pk] = (ingredient,
                                            valid_ingredients[ingredient.pk])
    return valid_ingredients
