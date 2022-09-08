from django_filters import rest_framework as filters
from recipes.models import Recipes, Tags


class RecipesFilter(filters.FilterSet):
    tags = filters.ModelMultipleChoiceFilter(
        queryset=Tags.objects.all(),
        field_name='tags__slug',
        to_field_name='slug'
    )
    is_favorited = filters.BooleanFilter(
        method='custom_favorited'
    )
    is_in_shopping_cart = filters.BooleanFilter(
        method='custom_shopping_cart'
    )

    class Meta:
        model = Recipes
        fields = ('tags', 'is_favorited', 'is_in_shopping_cart', 'author')

    def custom_favorited(self, queryset, name, value):
        user = self.request.user
        if value:
            return queryset.filter(favorite__user=user)
        return Recipes.objects.all()

    def custom_shopping_cart(self, queryset, name, value):
        user = self.request.user
        if value:
            return queryset.filter(shop_list__user=user)
        return Recipes.objects.all()
