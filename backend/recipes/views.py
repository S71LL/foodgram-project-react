from rest_framework import viewsets, status
from django_filters import rest_framework as filters
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.decorators import action
from django.http.response import HttpResponse
from django.db.models import Sum
from djoser.views import UserViewSet

from recipes.models import (Recipe, Ingredient,
                            Tag, Follow,
                            Favorite, ShoppingCart,
                            RecipeIngredient,
                            User)
from .serializers import (RecipeSerializer,
                          IngredientSerializer,
                          TagSerializer,
                          FollowAuthorSerializer,
                          FollowingSerializer,
                          FavoriteSerializer,
                          ShoppingCartSerializer
                          )
from .permissions import AuthorOrReadOnly
from .filters import IngredientFilter, RecipeFilter
from .paginations import CustomPaginator


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = TagSerializer
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all().order_by('-pub_date')
    serializer_class = RecipeSerializer
    permission_classes = (AuthorOrReadOnly,)
    pagination_class = CustomPaginator
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = RecipeFilter

    @action(detail=True, methods=['POST', 'DELETE'],
            permission_classes=(IsAuthenticated,))
    def favorite(self, request, **kwargs):
        recipe = get_object_or_404(Recipe, id=kwargs['pk'])
        if request.method == 'POST':
            serializer = FavoriteSerializer(data=request.data,
                                            context={'request': request,
                                                     'recipe': recipe},)
            serializer.is_valid(raise_exception=True)
            serializer.save(user=request.user, recipe=recipe)
            return Response(serializer.data,
                            status=status.HTTP_201_CREATED)
        get_object_or_404(Favorite, user=request.user,
                          recipe=recipe).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['POST', 'DELETE'],
            permission_classes=(IsAuthenticated,))
    def shopping_cart(self, request, **kwargs):
        recipe = get_object_or_404(Recipe, id=kwargs['pk'])
        if request.method == 'POST':
            serializer = ShoppingCartSerializer(data=request.data,
                                                context={'request': request,
                                                         'recipe': recipe})
            serializer.is_valid(raise_exception=True)
            serializer.save(user=request.user, recipe=recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        get_object_or_404(ShoppingCart, user=request.user,
                          recipe=recipe).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['GET'],
            permission_classes=(IsAuthenticated,))
    def download_shopping_cart(self, request, **kwargs):
        ingredients = (
            RecipeIngredient.objects
            .filter(recipe__shopping_cart__user=request.user)
            .values('ingredient').annotate(total_amount=Sum('amount'))
            .values_list('ingredient__name', 'total_amount',
                         'ingredient__measurement_unit')
        )
        file_list = []
        [file_list.append(
            '___ {} - {} {}'.format(*ingredient))
            for ingredient in ingredients]
        file = HttpResponse('Cписок покупок:\n' + '\n'.join(file_list),
                            content_type='text/plain')
        file['Content-Disposition'] = ('attachment; filename=Список покупок')
        return file


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = IngredientSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = IngredientFilter
    pagination_class = None


class CustomUserViesSet(UserViewSet):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    pagination_class = CustomPaginator

    @action(detail=False, methods=['GET'],
            permission_classes=(IsAuthenticated,))
    def subscriptions(self, request):
        page = self.paginate_queryset(
            User.objects.filter(follower__user=self.request.user)
        )
        serializer = FollowingSerializer(page, many=True,
                                         context={'request': request})
        return self.get_paginated_response(serializer.data)

    @action(detail=True, methods=['POST', 'DELETE'],
            permission_classes=(IsAuthenticated,))
    def subscribe(self, request, **kwargs):
        author = get_object_or_404(User, id=kwargs['id'])
        if request.method == 'POST':
            serializer = FollowAuthorSerializer(data=request.data,
                                                context={'request': request,
                                                         'author': author})
            serializer.is_valid(raise_exception=True)
            serializer.save(user=request.user, author=author)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        follow = get_object_or_404(Follow,
                                   user=request.user, author=author)
        follow.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
