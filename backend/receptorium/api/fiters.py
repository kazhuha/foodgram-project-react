from django_filters import rest_framework as filters
from recipes.models import Recipe


class RecipeFilter(filters.FilterSet):
    """Фильтрует рецепты по избранному, списку покупок,
    и тэгам"""
    is_favorited = filters.BooleanFilter(
        field_name='is_favorited',
        method='favorite_filter'
    )
    is_in_shopping_cart = filters.BooleanFilter(
        field_name='is_in_shopping_cart',
        method='shopping_cart_filter'
    )
    tags = filters.AllValuesMultipleFilter(field_name='tags__slug')

    def favorite_filter(self, queryset, name, value):
        recipes = Recipe.objects.filter(favorites__user=self.request.user)
        return recipes

    def shopping_cart_filter(self, queryset, name, value):
        recipes = Recipe.objects.filter(shopping_lists__user=self.request.user)
        return recipes

    class Meta:
        model = Recipe
        fields = ['author']
