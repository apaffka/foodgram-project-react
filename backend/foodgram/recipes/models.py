from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Ingredients(models.Model):
    name = models.CharField(
        blank=False
    )
    unit = models.CharField(
        max_length=32
    )


class Tags(models.Model):
    name = models.CharField(
        'Название тега',
        max_length=50,
        blank=False,
        help_text='Нам нужны теги, чтобы понять, что это за рецепт',
    )
    slug = models.SlugField(
        'Уникальный идентификатор тега',
        unique=True,
        blank=False,
        max_length=50
    )
    color = models.CharField(
        max_length=7,
        blank=False,
        default='#ffffff'
    )

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-slug']
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'


class Recipes(models.Model):
    name = models.CharField(
        'Название рецепта',
        max_length=150,
        help_text='Название рецепта',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes'
    )
    image = models.ImageField(
        'Изображение готового блюда',
        upload_to='recipes',
        blank=False,
    )
    text = models.TextField(
        'Описание приготовления блюда',
        max_length=2000,
        help_text='Подробно описать рецепт'
    )
    tags = models.ForeignKey(
        Tags,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='recipes',
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


class Follow(models.Model):
    pass


class Favourites(models.Model):
    pass


class Shoplist(models.Model):
    pass
