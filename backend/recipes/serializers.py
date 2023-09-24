import base64

from django.core.files.base import ContentFile
from rest_framework import serializers
from django.core.exceptions import ValidationError
from django.db.models import F

from recipes.models import (User,
                            Recipe,
                            Ingredient,
                            Tag,
                            RecipeIngredient,
                            Favorite,
                            ShoppingCart,
                            Follow
                            )

from recipes.models import RecipeIngredient
from recipes.validators import tags_validator, ingredients_validator
from . import constants


def create_recipe_ingredient(instance, ingredients):
    recipe_ingredient_objs = []
    for ingredient, amount in ingredients.values():
        recipe_ingredient_objs.append(
            RecipeIngredient(
                recipe=instance,
                ingredient=ingredient,
                amount=amount))
    RecipeIngredient.objects.bulk_create(recipe_ingredient_objs)


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class CustomUserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username',
                  'first_name', 'last_name',
                  'is_subscribed', 'password')

    def get_is_subscribed(self, obj):
        if (self.context.get('request')
           and not self.context['request'].user.is_anonymous):
            user = self.context['request'].user
            return user.following.filter(author=obj).exists()
        return False

    def create(self, validated_data):
        user = User(
            email=validated_data['email'],
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = '__all__'
        read_only_fields = ('__all__',)


class ShortRecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField(read_only=True)
    name = serializers.ReadOnlyField()
    cooking_time = serializers.ReadOnlyField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = ('__all__',)


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = '__all__'


class RecipeSerializer(serializers.ModelSerializer):
    ingredients = serializers.SerializerMethodField()
    image = Base64ImageField()
    author = CustomUserSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    text = serializers.CharField()
    name = serializers.CharField()
    cooking_time = serializers.IntegerField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags',
                  'author', 'ingredients',
                  'is_favorited', 'is_in_shopping_cart',
                  'name', 'image',
                  'text', 'cooking_time')

    def get_ingredients(self, recipe):
        ingredients = recipe.ingredients.values(
            "id", "name", "measurement_unit", amount=F("recipe__amount")
        )
        return ingredients

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if (request and not request.user.is_anonymous):
            return request.user.favorite.filter(recipe=obj).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if (request and not request.user.is_anonymous):
            return request.user.carts.filter(recipe=obj).exists()
        return False

    def validate(self, data):
        text = self.initial_data.get('text')
        name = self.initial_data.get('name')
        tags = self.initial_data.get('tags')
        ingredients = self.initial_data.get('ingredients')
        time = self.initial_data.get('cooking_time')
        if (not isinstance(text, str) or not isinstance(name, str)
           or not isinstance(time, int)):
            raise ValidationError('Неверное значение поля')
        if (not constants.MIN_COOKING_TIME > int(time)
           and int(time) > constants.MAX_COOKING_TIME):
            raise ValidationError('Неверное время приготовления')
        if len(name) > constants.NAME_MAX_LENGTH:
            raise ValidationError('Слишком длинное название')
        if not tags or not ingredients or not text or not name:
            raise ValidationError('Недостаточно данных')
        valid_tags = tags_validator(tags, Tag)
        valid_ingredients = ingredients_validator(ingredients, Ingredient)
        data.update(
            {
                'tags': valid_tags,
                'ingredients': valid_ingredients,
                'author': self.context.get('request').user,
            }
        )
        return data

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        instance = super().create(validated_data)
        instance.tags.set(tags)
        create_recipe_ingredient(instance, ingredients)
        return instance

    def update(self, instance, validated_data):
        instance.ingredients.clear()
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        instance.tags.set(tags)
        create_recipe_ingredient(instance, ingredients)
        return super().update(instance, validated_data)


class FollowAuthorSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField()
    author = serializers.ReadOnlyField()

    class Meta:
        model = Follow
        fields = ('user', 'author')

    def validate(self, data):
        if Follow.objects.filter(user=self.context.get('request').user,
                                 author=self.context.get('author')).exists():
            raise ValidationError('Пользователь уже подписан на автора')
        return data

    def to_representation(self, instance):
        return FollowingSerializer(instance.author,
                                   context=self.context).data


class FollowingSerializer(CustomUserSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id',
                  'username', 'first_name',
                  'last_name', 'is_subscribed',
                  'recipes', 'recipes_count')
        read_only_fields = ('__all__',)

    def get_recipes_count(self, obj):
        return obj.recipes.count()

    def get_recipes(self, obj):
        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
        recipes = obj.recipes.all()
        if limit:
            try:
                recipes = recipes[:int(limit)]
            except ValueError:
                raise Exception(message='limit must be a number')
        serializer = RecipeSerializer(recipes, context=self.context,
                                      many=True, read_only=True)
        return serializer.data


class FavoriteSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField()
    recipe = serializers.ReadOnlyField()

    class Meta:
        model = Favorite
        fields = ('user', 'recipe')

    def validate(self, data):
        if Favorite.objects.filter(user=self.context.get('request').user,
                                   recipe=self.context.get('recipe')).exists():
            raise ValidationError('Рецепт уже в избранном')
        return data

    def to_representation(self, instance):
        return ShortRecipeSerializer(instance.recipe,
                                     context=self.context).data


class ShoppingCartSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField()
    recipe = serializers.ReadOnlyField()

    class Meta:
        model = ShoppingCart
        fields = ('user', 'recipe')

    def validate(self, data):
        if ShoppingCart.objects.filter(user=self.context.get('request').user,
                                       recipe=self.context.get('recipe')
                                       ).exists():
            raise ValidationError('Рецепт уже в списке покупок')
        return data

    def to_representation(self, instance):
        return ShortRecipeSerializer(instance.recipe,
                                     context=self.context).data
