from django.contrib.auth import get_user_model
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator

NAME_MAX_LENGTH = 200
SLUG_MAX_LENGTH = 64
COLOR_MAX_LENGTH = 7
MIN_COOKING_TIME = 1
MAX_COOKING_TIME = 2880

User = get_user_model()


class Tag(models.Model):
    name = models.CharField(max_length=NAME_MAX_LENGTH)
    color = models.CharField(max_length=COLOR_MAX_LENGTH)
    slug = models.SlugField(max_length=SLUG_MAX_LENGTH, unique=True)

    class Meta:
        verbose_name = 'Тэг'

    def __str__(self):
        return f'{self.name}, цвет: {self.color}'


class Ingredient(models.Model):
    name = models.CharField(max_length=NAME_MAX_LENGTH)
    measurement_unit = models.CharField(max_length=NAME_MAX_LENGTH)

    class Meta:
        verbose_name = 'Ингредиент'
        constraints = (
            models.UniqueConstraint(
                fields=('name', 'measurement_unit'),
                name='unique_ingredient',
            ),
        )

    def __str__(self):
        return f'{self.name}, мера: {self.color}'


class Recipe(models.Model):
    name = models.CharField(max_length=NAME_MAX_LENGTH)
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
    cooking_time = models.PositiveIntegerField(
        validators=(MinValueValidator(MIN_COOKING_TIME),
                    MaxValueValidator(MAX_COOKING_TIME))
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient'
    )
    image = models.ImageField(upload_to='recipes/')

    class Meta:
        verbose_name = 'Рецепт'

    def __str__(self):
        return f'Рецепт {self.name}, автора {self.author}'


class RecipeIngredient(models.Model):
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    amount = models.FloatField()

    class Meta:
        verbose_name = 'Количество ингредиента'

    def __str__(self):
        return f'{self.ingredient} в количестве {self.amount}'


class Follow(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name='follower')
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='following')

    class Meta:
        verbose_name = 'Подписка на автор'
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'author'),
                name='unique_following',
            ),
        )

    def __str__(self):
        return f'{self.user} подписан на {self.author}'


class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name='favorite')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Рецепт в избранном'
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_favorite',
            ),
        )

    def __str__(self):
        return f'{self.recipe} в избранном у {self.user}'


class ShoppingCart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name='carts')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE,
                               related_name='shopping_cart')

    class Meta:
        verbose_name = 'Рецепт в списке покупок'
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_in_shopping_cart',
            ),
        )

    def __str__(self):
        return f'{self.recipe} в списке покупок у {self.user}'
