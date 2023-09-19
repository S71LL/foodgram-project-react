from django_filters import rest_framework as filters
from django.contrib.auth import get_user_model

from .models import Ingredient, Tag, Recipe


User = get_user_model()


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
    author = filters.ModelMultipleChoiceFilter(
        queryset=User.objects.all()
    )
    is_favorited = filters.BooleanFilter(
        method='is_favorited_filter')
    is_in_shopping_cart = filters.BooleanFilter(
        method='is_in_shopping_cart_filter')

    class Meta:
        model = Recipe
        fields = ('tags', 'author')

    def is_favorited_filter(self, queryset, value, _):
        user = self.request.user
        if value:
            return queryset.filter(favorite__user=user)
        return queryset

    def is_in_shopping_cart_filter(self, queryset, value, _):
        user = self.request.user
        if value:
            return queryset.filter(shopping_cart__user=user)
        return queryset
