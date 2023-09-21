from recipes.models import RecipeIngredient


def create_recipe_ingredient(instance, ingredients):
    recipe_ingredient_objs = [
        RecipeIngredient(
            recipe=instance,
            ingredient=ingredient['ingredient'],
            amount=ingredient['amount']) for ingredient in ingredients
    ]
    RecipeIngredient.objects.bulk_create(recipe_ingredient_objs)
