from django.shortcuts import get_object_or_404
from rest_framework import serializers

from recipes.models import Ingredient, RecipeIngredient


def ingredient_for_recipe_create(ingredient_list, recipe_obj):
    """Добавляет ингредиенты в рецепт при его создании
    или редактировании"""
    ingredient_obj_list = []
    for ingredient in ingredient_list:
        current_ingredient = get_object_or_404(
            Ingredient,
            id=ingredient['id']
        )
        ingredient_obj_list.append(
            RecipeIngredient(
                ingredient=current_ingredient,
                recipe=recipe_obj,
                amount=ingredient['amount']
            )
        )
    RecipeIngredient.objects.bulk_create(ingredient_obj_list)


def double_checker(list_of_arr: list):
    """Проверяет наличие повторяющихся елементов"""
    for arr in list_of_arr:
        for element in arr:
            if arr.count(element) > 1:
                raise serializers.ValidationError(
                        f'{element} уже добавлен в рецепт'
                    )
