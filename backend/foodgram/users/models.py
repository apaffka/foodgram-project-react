from django.contrib.auth.models import AbstractUser
from django.db import models


# Определяем пользовательскую модель
class User(AbstractUser):
    username = models.CharField(
        'Имя пользователя',
        max_length=150,
        unique=True,
        help_text='Letters, digits and @/./+/-/_ only.',
        error_messages={
            'unique': 'Пользователь с таким именем уже существует',
        },
    )
    email = models.EmailField(
        'Email',
        blank=False,
        unique=True,
        max_length=254
    )
    first_name = models.CharField(
        'Имя',
        max_length=150,
        blank=False
    )
    last_name = models.CharField(
        'Фамилия',
        max_length=150,
        blank=False
    )
    password = models.CharField(
        'Пароль',
        max_length=150
    )
