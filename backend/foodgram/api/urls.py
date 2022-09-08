from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (FavouriteViewSet, FollowAddViewSet, FollowListViewSet,
                    IngredientsViewSet, RecipesViewSet, ShopListDownload,
                    ShoplistViewSet, TagViewSet, UserViewSet)

router = DefaultRouter()

router.register(r'users/subscriptions', FollowListViewSet,
                basename='subscriptions')
router.register(r'users', UserViewSet, basename='users')
router.register(r'tags', TagViewSet, basename='tags')
router.register(r'recipes', RecipesViewSet, basename='recipes')
router.register(r'ingredients', IngredientsViewSet, basename='ingredients')

urlpatterns = [
    path('', include(router.urls)),
    path('recipes/download_shopping_cart/', ShopListDownload.as_view()),

    path('users/<id>/subscribe/', FollowAddViewSet.as_view(
        {'post': 'create', 'delete': 'destroy'}
    )),
    path('recipes/<id>/favorite/', FavouriteViewSet.as_view(
        {'post': 'create', 'delete': 'destroy'}
    )),
    path('recipes/<id>/shopping_cart/', ShoplistViewSet.as_view(
        {'post': 'create', 'delete': 'destroy'}
    )),
]
