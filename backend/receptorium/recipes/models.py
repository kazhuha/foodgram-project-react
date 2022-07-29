import webcolors

from django.core.validators import MinValueValidator
from django.forms import ValidationError
from django.db import models
from user.models import User

from .validators import validate_hex_color


class Ingredient(models.Model):
    """Модель ингредиентов"""
    name = models.CharField(
        max_length=100,
        blank=False,
        verbose_name='Название'
    )
    measurement_unit = models.CharField(
        max_length=10,
        blank=False,
        verbose_name='Единицы измерения'
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ['name']
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='unique ingredients'
            )
        ]

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'


class Tag(models.Model):
    """Модель тегов"""
    name = models.CharField(
        max_length=200,
        blank=False,
        unique=True,
        verbose_name='Название'
    )
    color_name = models.CharField(
        max_length=20,
        blank=False,
        unique=True,
        verbose_name='Цвет тега',
        help_text='Введите цвет на английском языке',
        validators=[validate_hex_color]
    )
    color = models.CharField(
        max_length=7,
        blank=True,
        verbose_name='Цветовой HEX-код',
        help_text='Не вводите значение, оно введется автоматически',
    )
    slug = models.SlugField(
        max_length=200,
        blank=False,
        unique=True,
        verbose_name='Slug'
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.color = webcolors.name_to_hex(self.color_name)
        super().save(*args, **kwargs)


class Recipe(models.Model):
    "Модель рецептов"
    author = models.ForeignKey(
        User,
        related_name='recipes',
        on_delete=models.CASCADE,
        verbose_name='Автор',
    )
    name = models.CharField(
        max_length=200,
        verbose_name='Название'
    )
    text = models.TextField(verbose_name='Рецепт')
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Тэги'
    )
    cooking_time = models.IntegerField(
        verbose_name='Время приготовления',
        help_text='Укажите время приготовления в минутах',
        validators=[MinValueValidator(1)]
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        related_name='recipes',
        verbose_name='Ингредиенты'
    )
    image = models.ImageField(
        upload_to='recipes/',
        verbose_name='Фото'
    )
    # fav_total = models.IntegerField(
    #     default=0
    # )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ['-pk']

    def __str__(self):
        return self.name

    # def save(self, *args, **kwargs):
    #     self.fav_total = self.favorites.all().count()
    #     super().save(*args, **kwargs)


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipes_ingredients',
        verbose_name='Рецепт'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='recipes_ingredients',
        verbose_name='Ингредиент'
    )
    amount = models.FloatField(
        verbose_name='Количество',
        validators=[MinValueValidator(0.1)]
    )

    class Meta:
        verbose_name = 'Ингредиент для рецепта'
        verbose_name_plural = 'Ингредиенты для рецептов'

    def __str__(self):
        return f'{self.recipe} {self.ingredient}'


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор'
    )

    class Meta:
        verbose_name = 'Подписки'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author', ], name='uniqe_follow'
            ),
        ]

    def __str__(self):
        return f'{self.user} {self.author}'

    def clean(self):
        if self.user == self.author:
            raise ValidationError('Нельзя подписываться на себя')


class ShoppingList(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_lists',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shopping_lists',
        verbose_name='Рецепт'
    )

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe', ], name='uniqe_shopping_list'
            )
        ]

    def __str__(self):
        return f'{self.user} {self.recipe}'


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Рецепт'
    )

    class Meta:
        verbose_name = 'Список избранного'
        verbose_name_plural = 'Списки избранного'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe', ], name='uniqe_favorite'
            )
        ]

    def __str__(self):
        return f'{self.user} {self.recipe}'
