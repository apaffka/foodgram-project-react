from django.conf import settings
from django.db import models


class Ingredients(models.Model):
    name = models.CharField(
        'Ингредиент',
        max_length=200,
        blank=False
    )
    measurement_unit = models.CharField(
        'Единица измерения',
        max_length=200,
        blank=False
    )

    class Meta:
        ordering = ['name']
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


class Tags(models.Model):
    name = models.CharField(
        'Название тега',
        max_length=200,
        blank=False,
        help_text='Нам нужны теги, чтобы понять, что это за рецепт',
    )
    color = models.CharField(
        'Цвет',
        max_length=7,
        blank=False,
        default='#ffffff'
    )
    slug = models.SlugField(
        'Уникальный идентификатор тега',
        unique=True,
        blank=False,
        max_length=200
    )

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['slug']
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'


class Recipes(models.Model):
    name = models.CharField(
        'Название рецепта',
        max_length=150,
        help_text='Название рецепта',
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор'
    )
    image = models.ImageField(
        'Изображение готового блюда',
        blank=False,
    )
    text = models.TextField(
        'Описание приготовления блюда',
        max_length=2000,
        help_text='Подробно описать рецепт'
    )
    tags = models.ManyToManyField(
        Tags,
        through='RecipeTag'
    )
    ingredients = models.ManyToManyField(
        Ingredients,
        through='RecipeIngredient'
    )
    cooking_time = models.PositiveSmallIntegerField(
        'Время приготовления'
    )
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'


class RecipeIngredient(models.Model):
    recipes = models.ForeignKey(
        Recipes,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='ingredients_recipe'
    )
    ingredients = models.ForeignKey(
        Ingredients,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент',
        related_name='recipe_ingredient'
    )
    amount = models.PositiveSmallIntegerField(
        'Численное количество ингредиента',
        blank=True
    )

    class Meta:
        verbose_name = 'Рецепт/Ингредиент'
        verbose_name_plural = 'Рецепты/Ингредиенты'

    def __str__(self):
        return f'{self.recipes} добавлен ингредиент {self.ingredients}'


class RecipeTag(models.Model):
    recipes = models.ForeignKey(
        Recipes,
        on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )
    tags = models.ForeignKey(
        Tags,
        on_delete=models.CASCADE,
        verbose_name='Тег'
    )

    class Meta:
        verbose_name = 'Рецепт/Тег'
        verbose_name_plural = 'Рецепты/Теги'

    def __str__(self):
        return f'{self.recipes} присвоен тег: {self.tags}'


class Follow(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик'
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='followed',
        verbose_name='На кого подписан'
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self):
        return f'{self.user}, подписан на {self.author}'


class Favourites(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='lover',
        verbose_name='Кто выбрал рецепт'
    )
    recipe = models.ForeignKey(
        Recipes,
        on_delete=models.CASCADE,
        related_name='favorite',
        verbose_name='Избранный рецепт'

    )

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'


class Shoplist(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='buyer',
        verbose_name='Будет покупать'
    )
    recipe = models.ForeignKey(
        Recipes,
        on_delete=models.CASCADE,
        related_name='shop_list',
        verbose_name='Что будет покупать'
    )

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Список покупок'
