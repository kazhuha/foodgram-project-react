from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Модель пользователя"""
    password = models.CharField(
        max_length=150, blank=False, verbose_name='Пароль'
    )
    email = models.EmailField(
        max_length=254, blank=False, unique=True, verbose_name='Почта'
    )
    first_name = models.CharField(
        max_length=150, blank=False, verbose_name='Имя'
    )
    last_name = models.CharField(
        max_length=150, blank=False, verbose_name='Фамилия'
    )

    REQUIRED_FIELDS = ['first_name', 'last_name', 'username']
    USERNAME_FIELD = 'email'
