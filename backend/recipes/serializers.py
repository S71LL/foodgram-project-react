import base64

from django.core.files.base import ContentFile
from rest_framework import serializers
from django.core.exceptions import ValidationError

from recipes.models import (User,
                            Recipe,
                            Ingredient,
                            Tag,
                            RecipeIngredient,
                            Favorite,
                            ShoppingCart,
                            Follow
                            )
from recipes.validators import tags_validator, ingredients_validator
from . import constants


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
        extra_kwargs = {
            'password': {'write_only': True}
        }

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

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = ('__all__',)


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = '__all__'


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.CharField(source='ingredient.name')
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit')

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeIngredientCreateSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        source='ingredient',
        queryset=Ingredient.objects.all()
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    ingredients = RecipeIngredientSerializer(many=True,
                                             source='ingredient')
    image = Base64ImageField()
    author = CustomUserSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags',
                  'author', 'ingredients',
                  'is_favorited', 'is_in_shopping_cart',
                  'name', 'image',
                  'text', 'cooking_time')

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


class RecipeCreateSerializer(serializers.ModelSerializer):
    ingredients = RecipeIngredientCreateSerializer(many=True)
    image = Base64ImageField()
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True)
    cooking_time = serializers.IntegerField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags',
                  'ingredients',
                  'name', 'image',
                  'text', 'cooking_time')

    def create_recipe_ingredient(self, instance, ingredients):
        recipe_ingredient_objs = [
            RecipeIngredient(
                recipe=instance,
                ingredient=ingredient['ingredient'],
                amount=ingredient['amount']) for ingredient in ingredients
        ]
        RecipeIngredient.objects.bulk_create(recipe_ingredient_objs)

    def validate(self, data):
        text = data.get('text')
        name = data.get('name')
        tags = data.get('tags')
        ingredients = data.get('ingredients')
        try:
            cooking_time = int(data.get('cooking_time'))
        except ValueError:
            raise ValidationError('Время приготовления должно '
                                  'быть целым числом')
        if not isinstance(text, str) or not isinstance(name, str):
            raise ValidationError(
                'Описание и название рецепта должны быть текстом')
        if (not constants.MIN_COOKING_TIME > int(cooking_time)
           and int(cooking_time) > constants.MAX_COOKING_TIME):
            raise ValidationError('Время приготовления не может быть '
                                  'меньше 1 или больше 2880')
        if len(name) > constants.NAME_MAX_LENGTH:
            raise ValidationError('Слишком длинное название')
        if not tags:
            raise ValidationError('У рецепта должны быть теги')
        if not ingredients:
            raise ValidationError('В рецепте должен быть '
                                  'хотя бы один ингредиент')
        if not text:
            raise ValidationError('У рецепта должно быть описание')
        if not name:
            raise ValidationError('У рецепта должно быть название')
        tags_validator(tags, Tag)
        ingredients_validator(ingredients, Ingredient)
        return data

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        instance = super().create(validated_data)
        instance.tags.set(tags)
        self.create_recipe_ingredient(instance, ingredients)
        return instance

    def update(self, instance, validated_data):
        instance.ingredients.clear()
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        instance.tags.set(tags)
        self.create_recipe_ingredient(instance, ingredients)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        return RecipeSerializer(instance,
                                context=self.context).data


class FollowAuthorSerializer(serializers.ModelSerializer):

    class Meta:
        model = Follow
        fields = ('user', 'author')

    def validate(self, data):
        if data['user'].following.filter(author=data['author']).exists():
            raise ValidationError('Пользователь уже подписан на автора')
        if data['user'] == data['author']:
            raise ValidationError('Нельзя подписываться на самого себя')
        return data

    def to_representation(self, instance):
        return FollowingSerializer(instance.author,
                                   context=self.context).data


class FollowingSerializer(CustomUserSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = '__all__'
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

    class Meta:
        model = Favorite
        fields = '__all__'

    def validate(self, data):
        if data['user'].favorite.filter(recipe=data['recipe']).exists():
            raise ValidationError('Рецепт уже в избранном')
        return data

    def to_representation(self, instance):
        return ShortRecipeSerializer(instance.recipe,
                                     context=self.context).data


class ShoppingCartSerializer(serializers.ModelSerializer):

    class Meta:
        model = ShoppingCart
        fields = '__all__'

    def validate(self, data):
        if data['user'].carts.filter(recipe=data['recipe']).exists():
            raise ValidationError('Рецепт уже в списке покупок')
        return data

    def to_representation(self, instance):
        return ShortRecipeSerializer(instance.recipe,
                                     context=self.context).data
