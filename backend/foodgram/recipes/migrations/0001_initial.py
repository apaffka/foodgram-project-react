# Generated by Django 3.2.15 on 2022-09-01 11:36

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Favourites',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='Follow',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='Shoplist',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='Tags',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Нам нужны теги, чтобы понять, что это за рецепт', max_length=50, verbose_name='Название тега')),
                ('slug', models.SlugField(unique=True, verbose_name='Уникальный идентификатор тега')),
                ('color', models.CharField(default='#ffffff', max_length=7)),
            ],
        ),
        migrations.CreateModel(
            name='Recipes',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Название рецепта', max_length=150, verbose_name='Название рецепта')),
                ('image', models.ImageField(upload_to='recipes', verbose_name='Изображение готового блюда')),
                ('text', models.TextField(help_text='Подробно описать рецепт', max_length=2000, verbose_name='Описание приготовления блюда')),
                ('cooking_time', models.IntegerField()),
                ('pub_date', models.DateTimeField(auto_now_add=True, verbose_name='Дата публикации')),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recipes', to=settings.AUTH_USER_MODEL)),
                ('tags', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='recipes.tags')),
            ],
        ),
    ]