from django.contrib import admin

from .models import (Favourites, Follow, Ingredients, RecipeIngredient,
                     Recipes, RecipeTag, Shoplist, Tags)


class RecipesAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'author', 'text', 'cooking_time', 'pub_date'
    )
    search_fields = ('text',)
    list_filter = ('pub_date',)
    empty_value_display = '-пусто-'


class TagsAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'slug', 'color'
    )
    search_fields = ('name',)
    list_filter = ('slug',)
    empty_value_display = '-пусто-'


class IngredientsAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'measurement_unit'
    )
    search_fields = ('name',)
    empty_value_display = '-пусто-'


class RecipeTagAdmin(admin.ModelAdmin):
    list_display = (
        'recipes', 'tags'
    )


class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = (
        'recipes', 'ingredients', 'amount'
    )


class FollowAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'author'
    )


class FavouritesAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'recipe'
    )


class ShoplistAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'recipe'
    )


admin.site.register(Recipes, RecipesAdmin)
admin.site.register(Tags, TagsAdmin)
admin.site.register(Ingredients, IngredientsAdmin)
admin.site.register(RecipeTag, RecipeTagAdmin)
admin.site.register(RecipeIngredient, RecipeIngredientAdmin)

admin.site.register(Follow, FollowAdmin)
admin.site.register(Favourites, FavouritesAdmin)
admin.site.register(Shoplist, ShoplistAdmin)