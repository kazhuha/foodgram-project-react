from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response

from recipes.models import Recipe
from .serializers import RecipeForFavoriteSubscriptionsSerializer


def object_add_or_delete(model, request, pk):
    """Функция для создания или удаления объекта из модели"""
    recipe = get_object_or_404(Recipe, pk=pk)
    if request.method == 'POST':
        _, created = model.objects.get_or_create(
            user=request.user, recipe=recipe
        )
        if not created:
            return Response(
                data={"errors": "Рецепт уже добавлен в список"},
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer = RecipeForFavoriteSubscriptionsSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    if not model.objects.filter(
        user=request.user, recipe=recipe
    ).exists():
        return Response(
                data={"errors": "Рецепт отсутствует в списке"},
                status=status.HTTP_400_BAD_REQUEST
            )
    model.objects.get(user=request.user, recipe=recipe).delete()
    return Response(status=status.HTTP_204_NO_CONTENT)
