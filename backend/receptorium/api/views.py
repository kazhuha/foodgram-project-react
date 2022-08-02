from django.shortcuts import get_object_or_404
from django.db.models import Sum
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from recipes.models import (Favorite, Follow, Ingredient, Recipe,
                            RecipeIngredient, ShoppingList, Tag)
from user.models import User
from .fiters import RecipeFilter
from .functions import object_add_or_delete
from .permissions import IsAuthorOrAuthenticatedOrReadOnly
from .serializers import (IngredientSerializer, RecipeCreateSerializer,
                          RecipeSerializer, SubscriptionsSerializer,
                          TagSerializer)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для ингредиентов"""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = (filters.SearchFilter,)
    search_fields = ('^name',)
    permission_classes = [IsAuthenticatedOrReadOnly, ]


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для тэгов"""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, ]
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет для рецептов"""
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    permission_classes = [IsAuthorOrAuthenticatedOrReadOnly]
    pagination_class = LimitOffsetPagination

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return RecipeSerializer
        return RecipeCreateSerializer


    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(methods=['post', 'delete'], detail=True)
    def favorite(self, request, pk):
        return object_add_or_delete(Favorite, request, pk)

    @action(methods=['post', 'delete'], detail=True)
    def shopping_cart(self, request, pk):
        return object_add_or_delete(ShoppingList, request, pk)

    @action(methods=['get'], detail=False)
    def download_shopping_cart(self, request):
        ingredients = RecipeIngredient.objects.filter(
            recipe__shopping_lists__user=request.user
        ).values(
            'ingredient__name', 'ingredient__measurement_unit'
        ).annotate(ingredient_sum=Sum('amount')).values_list(
            'ingredient__name',
            'ingredient__measurement_unit',
            'ingredient_sum'
        )
        text = ''
        for ingredient in ingredients:
            text += f'{ingredient[0]} - {ingredient[2]} {ingredient[1]}\r\n'
        response = HttpResponse(text, content_type='text/plain,charset=utf8')
        response['Content-Disposition'] = 'attachment; filename=shopping.txt'
        return response


class CustomUserViewSet(UserViewSet):
    """Кастомный вьюсет для юзера"""
    @action(methods=['get'], detail=False)
    def subscriptions(self, request):
        following_users = User.objects.filter(following__user=request.user)
        page = self.paginate_queryset(following_users)
        if page is not None:
            serialaizer = SubscriptionsSerializer(
                page, many=True, context={'request': request}
            )
            return self.get_paginated_response(serialaizer.data)
        serialaizer = SubscriptionsSerializer(
            following_users, many=True, context={'request': request}
        )
        return Response(serialaizer.data, status=status.HTTP_200_OK)

    @action(methods=['post', 'delete'], detail=True)
    def subscribe(self, request, id):
        following_user = get_object_or_404(User, id=id)
        if request.user == following_user:
            return Response(
                data={"error": "Нельзя подписываться на самого себя"},
                status=status.HTTP_400_BAD_REQUEST
            )
        if request.method == 'POST':
            _, created = Follow.objects.get_or_create(
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
        if not Follow.objects.filter(
            user=request.user, author=following_user
        ).exists():
            return Response(
                data={"errors": "Автор отсутствует в списке"},
                status=status.HTTP_400_BAD_REQUEST
            )
        Follow.objects.get(user=request.user, author=following_user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
