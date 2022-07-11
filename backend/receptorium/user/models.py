from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    password = models.CharField(max_length=150)

    REQUIRED_FIELDS = ['email', 'first_name', 'last_name']
