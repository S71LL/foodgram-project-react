from django_filters import rest_framework as filters

from .models import Tag, Recipe, Ingredient


class IngredientFilter(filters.FilterSet):
    name = filters.CharFilter(field_name='name', lookup_expr='startswith')

    class Meta:
        model = Ingredient
        fields = ('name', )


class RecipeFilter(filters.FilterSet):
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all()
    )
    is_favorited = filters.BooleanFilter(
        method='is_favorited_filter')
    is_in_shopping_cart = filters.BooleanFilter(
        method='is_in_shopping_cart_filter')

    class Meta:
        model = Recipe
        fields = ('tags', 'author')

    def is_favorited_filter(self, queryset, _, value):
        if value:
            return queryset.filter(in_favorites__user=self.request.user)
        return queryset

    def is_in_shopping_cart_filter(self, queryset, _, value):
        if value:
            return queryset.filter(shopping_cart__user=self.request.user)
        return queryset
