import base64

from django.core.files.base import ContentFile
from rest_framework import serializers

from recipes.models import (User,
                            Recipe,
                            Ingredient,
                            Tag,
                            RecipeIngredient,
                            Favorite,
                            ShoppingCart,
                            Follow
                            )
from core.services import create_recipe_ingredient


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
                  'is_subscribed')

    def get_is_subscribed(self, obj):
        if (self.context.get('request')
           and not self.context['request'].user.is_anonymous):
            user = self.context['request'].user
            return user.follower.filter(author=obj).exists()
        return False


class CustomUserCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('email',
                  'id',
                  'username',
                  'first_name',
                  'last_name',
                  'password')

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


class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField()
    new_password = serializers.CharField()

    def update(self, instance, validated_data):
        if not instance.check_password(validated_data['current_password']):
            raise serializers.ValidationError()
        instance.set_password(validated_data['new_password'])
        instance.save()
        return validated_data


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = '__all__'


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.CharField(source='ingredient.name')
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit')

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    ingredients = RecipeIngredientSerializer(many=True,
                                             source='recipeingredient_set')
    image = Base64ImageField()
    author = CustomUserSerializer(read_only=True)
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
        if (self.context.get('request')
           and not self.context['request'].user.is_anonymous):
            user = self.context['request'].user
            return user.favorite.filter(recipe=obj).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        if (self.context.get('request')
           and not self.context['request'].user.is_anonymous):
            user = self.context['request'].user
            return user.carts.filter(recipe=obj).exists()
        return False


class ShortRecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField(read_only=True)
    name = serializers.ReadOnlyField()
    cooking_time = serializers.ReadOnlyField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = '__all__'


class RecipeIngredientCreateSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        source='ingredient',
        queryset=Ingredient.objects.all()
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class RecipeCreateSerializer(serializers.ModelSerializer):
    ingredients = RecipeIngredientCreateSerializer(many=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('name',
                  'cooking_time',
                  'text',
                  'tags',
                  'image',
                  'ingredients')

    def validate(self, obj):
        inrgedient_list = [
            item['ingredient'] for item in obj.get('ingredients')
        ]
        unique_ingredient_list = set(inrgedient_list)
        if len(inrgedient_list) != len(unique_ingredient_list):
            raise serializers.ValidationError(
                'Only unique ingredients required'
            )
        return obj

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        instance = super().create(validated_data)
        instance.tags.set(tags)
        create_recipe_ingredient(instance, ingredients)
        return instance

    def update(self, instance, validated_data):
        instance.ingredients.clear()
        instance.tags.clear
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        instance.tags.set(tags)
        create_recipe_ingredient(instance, ingredients)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        return RecipeSerializer(instance,
                                context=self.context).data


class FollowAuthorSerializer(serializers.ModelSerializer):
    email = serializers.ReadOnlyField(source='author.email')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')
    username = serializers.ReadOnlyField(source='author.username')
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = Follow
        fields = ('email', 'id',
                  'username', 'first_name',
                  'last_name', 'is_subscribed')

    def get_is_subscribed(self, obj):
        if (self.context.get('request')
           and not self.context['request'].user.is_anonymous):
            user = self.context['request'].user
            return user.follower.filter(author=obj.author).exists()
        return False


class FollowingSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id',
                  'username', 'first_name',
                  'last_name', 'is_subscribed',
                  'recipes', 'recipes_count')

    def get_is_subscribed(self, obj):
        if (self.context.get('request')
           and not self.context['request'].user.is_anonymous):
            user = self.context['request'].user
            return user.follower.filter(author=obj).exists()
        return False

    def get_recipes_count(self, obj):
        return obj.recipes.count()

    def get_recipes(self, obj):
        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
        recipes = obj.recipes.all()
        if limit:
            recipes = recipes[:int(limit)]
        serializer = RecipeSerializer(recipes, context=self.context,
                                      many=True, read_only=True)
        return serializer.data


class FavoriteSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField()
    recipe = serializers.ReadOnlyField()

    class Meta:
        model = Favorite
        fields = ('user', 'recipe')

    def to_representation(self, instance):
        return ShortRecipeSerializer(instance,
                                     context=self.context).data


class ShoppingCartSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField()
    recipe = serializers.ReadOnlyField()

    class Meta:
        model = ShoppingCart
        fields = ('user', 'recipe')

    def to_representation(self, instance):
        return ShortRecipeSerializer(instance,
                                     context=self.context).data
