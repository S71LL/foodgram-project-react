from django.urls import path, include
from rest_framework import routers

from recipes.views import (RecipeViewSet,
                           IngredientViewSet,
                           TagViewSet,
                           CustomUserViesSet)

router = routers.DefaultRouter()

router.register(r'recipes', RecipeViewSet, basename='recipes')
router.register(r'ingredients', IngredientViewSet, basename='ingredients')
router.register(r'tags', TagViewSet, basename='tags')
router.register(r'users', CustomUserViesSet, basename='users')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
]
