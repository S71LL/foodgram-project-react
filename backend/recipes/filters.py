from django_filters import rest_framework as filters
from django.contrib.auth import get_user_model
from rest_framework.filters import SearchFilter

from .models import Tag, Recipe


User = get_user_model()


class IngredientFilter(SearchFilter):
    search_param = 'name'


class RecipeFilter(filters.FilterSet):
    tags = filters.AllValuesMultipleFilter(
        field_name='tags__slug',
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
        user = self.request.user
        if value:
            return queryset.filter(favorite__user=user)
        return queryset

    def is_in_shopping_cart_filter(self, queryset, _, value):
        user = self.request.user
        if value:
            return queryset.filter(shopping_cart__user=user)
        return queryset
