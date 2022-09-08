from django.urls import include, path
from recipes.views import (FavouriteViewSet, IngredientsViewSet,
                           RecipesViewSet, ShopListDownload, ShoplistViewSet,
                           TagViewSet)
from rest_framework.routers import DefaultRouter
from users.views import FollowAddViewSet, FollowListViewSet, UserViewSet

router = DefaultRouter()

router.register(r'users/subscriptions', FollowListViewSet,
                basename='subscriptions')
router.register(r'users', UserViewSet, basename='users')
router.register(r'tags', TagViewSet, basename='tags')
router.register(r'recipes', RecipesViewSet, basename='recipes')
router.register(r'ingredients', IngredientsViewSet, basename='ingredients')

urlpatterns = [
    path('recipes/download_shopping_cart/', ShopListDownload.as_view()),
    path('', include(router.urls)),
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
