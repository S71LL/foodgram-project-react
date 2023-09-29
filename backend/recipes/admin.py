from django.contrib import admin

from recipes.models import (Tag,
                            Recipe,
                            Ingredient,
                            RecipeIngredient,
                            Follow,
                            ShoppingCart,
                            Favorite,
                            User)
from recipes.forms import RecipeForm, RecipeIngredientInLineFormSet, FollowForm


class RecipeIngredientInLine(admin.StackedInline):
    model = RecipeIngredient
    formset = RecipeIngredientInLineFormSet
    extra = 1


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'first_name',
                    'last_name', 'email')
    search_fields = ('username', 'email',)
    list_filter = ('username', 'email',)
    exclude = ('password',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug', 'color')
    list_filter = ('name',)
    search_fields = ('name',)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    form = RecipeForm
    inlines = (RecipeIngredientInLine, )
    list_display = ('pk', 'name', 'author', 'in_favorites')
    search_fields = ('name',)
    list_filter = ('name', 'author', 'tags',)

    @admin.display(description='Раз в избранном')
    def in_favorites(self, obj):
        return obj.in_favorites.count()


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'measurement_unit')
    list_filter = ('name',)
    search_fields = ('name',)


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'recipe', 'ingredient', 'amount',)
    list_filter = ('recipe', 'ingredient',)
    search_fields = ('name',)


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    form = FollowForm
    list_display = ('user', 'author')
    list_filter = ('author',)
    search_fields = ('user',)


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')
    list_filter = ('user',)
    search_fields = ('user',)


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')
    list_filter = ('user',)
    search_fields = ('user',)
