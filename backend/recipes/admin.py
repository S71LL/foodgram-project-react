from django.contrib import admin

from recipes.models import (Tag,
                            Recipe,
                            Ingredient,
                            RecipeIngredient,
                            Follow,
                            ShoppingCart)


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    pass


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    inlines = (RecipeIngredientInline, )
    list_display = ('pk', 'name', 'author', 'in_favorites')
    list_filter = ('name', 'author', 'tags')

    @admin.display(description='In favorite')
    def in_favorites(self, obj):
        return obj.favorite.count()


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'measurement_unit')
    list_filter = ('name', )
    search_fields = ('name', )


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    pass


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    pass
