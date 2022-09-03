from django.contrib import admin

from .models import Tags, Recipes


class RecipesAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'author', 'text', 'tags', 'cooking_time', 'pub_date'
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


admin.site.register(Recipes, RecipesAdmin)
admin.site.register(Tags, TagsAdmin)
