from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Tag(models.Model):
    name = models.CharField(max_length=200)
    color = models.CharField(max_length=7)
    slug = models.SlugField(max_length=64, unique=True)


class Ingredient(models.Model):
    name = models.CharField(max_length=200)
    measurement_unit = models.CharField(max_length=200)


class Recipe(models.Model):
    name = models.CharField(max_length=200)
    cooking_time = models.IntegerField()
    text = models.TextField()
    tags = models.ManyToManyField(Tag)
    pub_date = models.DateTimeField(
        auto_now_add=True
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient'
    )
    image = models.ImageField(upload_to='recipes/')


class RecipeIngredient(models.Model):
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    amount = models.FloatField()


class Follow(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name='follower')
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='following')

    class Meta:
        unique_together = ('user', 'author')


class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE,
                               related_name='favorite')

    class Meta:
        unique_together = ('user', 'recipe')


class ShoppingCart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE,
                               related_name='shopping_cart')

    class Meta:
        unique_together = ('user', 'recipe')
