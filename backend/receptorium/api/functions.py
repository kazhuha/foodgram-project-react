from django.shortcuts import get_object_or_404
from recipes.models import Follow, Recipe
from rest_framework import status
from rest_framework.response import Response
from user.models import User

from .serializers import (RecipeForFavoriteSubscriptionsSerializer,
                          SubscriptionsSerializer)


def object_add_or_delete(model, request, pk):
    if model == Follow:
        following_user = get_object_or_404(User, id=pk)
        if request.user == following_user:
            return Response(
                data={"error": "Нельзя подписываться на самого себя"},
                status=status.HTTP_400_BAD_REQUEST
            )
        if request.method == 'POST':
            obj, created = model.objects.get_or_create(
                user=request.user, author=following_user
            )
            if not created:
                return Response(
                    data={"errors": "Автор уже добавлен в список"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            serializer = SubscriptionsSerializer(
                following_user, context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if not model.objects.filter(
            user=request.user, author=following_user
        ).exists():
            return Response(
                data={"errors": "Автор отсутствует в списке"},
                status=status.HTTP_400_BAD_REQUEST
            )
        object = model.objects.get(user=request.user, author=following_user)
        object.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    recipe = get_object_or_404(Recipe, pk=pk)
    if request.method == 'POST':
        obj, created = model.objects.get_or_create(
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
    object = model.objects.get(
        user=request.user, recipe=recipe
    )
    object.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)
