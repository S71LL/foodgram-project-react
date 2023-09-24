from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import (MaxValueValidator,
                                    MinValueValidator,
                                    RegexValidator)
from django.db.models import F, Q

from . import constants


class User(AbstractUser):
    username = models.CharField(max_length=constants.USER_FIELDS_MAX_LENGTH,
                                unique=True,
                                validators=(RegexValidator(
                                    constants.USERNAME_REGEX),),
                                verbose_name='Имя пользователя'
                                )
    first_name = models.CharField(max_length=constants.USER_FIELDS_MAX_LENGTH,
                                  verbose_name='Имя')
    last_name = models.CharField(max_length=constants.USER_FIELDS_MAX_LENGTH,
                                 verbose_name='Фамилия')
    email = models.EmailField(unique=True,
                              max_length=constants.EMAIL_MAX_LENGTH,
                              verbose_name='Электронна почта')
    password = models.CharField(max_length=constants.USER_FIELDS_MAX_LENGTH,
                                verbose_name='Пароль')
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name', 'password']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username


class Tag(models.Model):
    name = models.CharField(max_length=constants.NAME_MAX_LENGTH,
                            verbose_name='Название тега')
    color = models.CharField(max_length=constants.COLOR_MAX_LENGTH,
                             validators=(RegexValidator(
                                 constants.COLOR_REGEX),),
                             verbose_name='Цвет тега')
    slug = models.SlugField(max_length=constants.SLUG_MAX_LENGTH,
                            unique=True,
                            validators=(RegexValidator(
                                constants.TAGS_SLUG_REGEX),),
                            verbose_name='Слаг тега')

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'

    def __str__(self):
        return f'{self.name}, цвет: {self.color}'


class Ingredient(models.Model):
    name = models.CharField(max_length=constants.NAME_MAX_LENGTH,
                            verbose_name='Название ингредиента')
    measurement_unit = models.CharField(max_length=constants.NAME_MAX_LENGTH,
                                        verbose_name='Единица измерения')

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        constraints = (
            models.UniqueConstraint(
                fields=('name', 'measurement_unit'),
                name='unique_ingredient',
            ),
        )

    def __str__(self):
        return f'{self.name}, мера: {self.measurement_unit}'


class Recipe(models.Model):
    name = models.CharField(max_length=constants.NAME_MAX_LENGTH,
                            verbose_name='Название рецепта')
    text = models.TextField(verbose_name='Текст рецепта')
    tags = models.ManyToManyField(Tag,
                                  verbose_name='Тег рецепта')
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор'
    )
    cooking_time = models.PositiveIntegerField(
        validators=(MinValueValidator(constants.MIN_COOKING_TIME),
                    MaxValueValidator(constants.MAX_COOKING_TIME)),
        verbose_name='Время приготовления'
    )
    ingredients = models.ManyToManyField(
        verbose_name='Ингредиент',
        related_name='recipes',
        to=Ingredient,
        through='recipes.RecipeIngredient'
    )
    image = models.ImageField(upload_to='recipes/',
                              verbose_name='Картинка')

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return f'Рецепт {self.name}, автора {self.author}'


class RecipeIngredient(models.Model):
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE,
                                   related_name='recipe',
                                   verbose_name='Ингредиент')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE,
                               related_name='ingredient',
                               verbose_name='Рецепт')
    amount = models.PositiveSmallIntegerField(MinValueValidator(
        constants.MIN_INGREDIENT_VALUE),)

    class Meta:
        verbose_name = 'Количество ингредиента'
        verbose_name_plural = 'Количество ингредиентов'

    def __str__(self):
        return f'{self.ingredient} в количестве {self.amount}'


class Follow(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name='following',
                             verbose_name='Подписчик')
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='follower',
                               verbose_name='Автор')

    class Meta:
        verbose_name = 'Подписка на автор'
        verbose_name_plural = 'Подписки на авторов'
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'author'),
                name='unique_following',
            ),
            models.CheckConstraint(check=~Q(author=F('user')),
                                   name='You should not following yourself'),
        )

    def __str__(self):
        return f'{self.user} подписан на {self.author}'


class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name='favorite',
                             verbose_name='Пользователь')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE,
                               related_name='in_favorites',
                               verbose_name='Рецепт')

    class Meta:
        verbose_name = 'Рецепт в избранном'
        verbose_name_plural = 'Рецепты в избранном'
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
                             related_name='carts',
                             verbose_name='Пользователь')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE,
                               related_name='shopping_cart',
                               verbose_name='Рецепт')

    class Meta:
        verbose_name = 'Рецепт в списке покупок'
        verbose_name_plural = 'Рецепты в списке покупок'
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_in_shopping_cart',
            ),
        )

    def __str__(self):
        return f'{self.recipe} в списке покупок у {self.user}'
