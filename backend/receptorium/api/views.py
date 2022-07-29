from django.db.models import Sum
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from recipes.models import (Favorite, Follow, Ingredient, Recipe,
                            RecipeIngredient, ShoppingList, Tag)
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from user.models import User

from .fiters import RecipeFilter
from .permissions import IsAuthorOrReadOnly
from .serializers import (IngredientSerializer, RecipeCreateSerializer,
                          RecipeSerializer, SubscriptionsSerializer,
                          TagSerializer)
from .functions import object_add_or_delete


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = (filters.SearchFilter,)
    search_fields = ('^name',)
    permission_classes = [IsAuthenticatedOrReadOnly, ]


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, ]
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    permission_classes = [IsAuthenticatedOrReadOnly, ]

    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'destroy']:
            self.permission_classes = [IsAuthorOrReadOnly]
        return super(RecipeViewSet, self).get_permissions()

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
        for i in ingredients:
            text += f'{i[0]} - {i[2]} {i[1]}\r\n'
        response = HttpResponse(text, content_type='text/plain,charset=utf8')
        response['Content-Disposition'] = 'attachment; filename=shopping.txt'
        return response


class CustomUserViewSet(UserViewSet):
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
        return object_add_or_delete(Follow, request, id)
