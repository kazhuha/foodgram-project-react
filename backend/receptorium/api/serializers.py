from djoser.serializers import UserSerializer
from rest_framework import serializers
from drf_extra_fields.fields import Base64ImageField

from api.utils import double_checker, ingredient_for_recipe_create
from recipes.models import (Favorite, Follow, Ingredient, Recipe,
                            RecipeIngredient, ShoppingList, Tag)
from user.models import User


class CustomUserSerializer(UserSerializer):
    """Кастомный сериализатор для модели юзера"""
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed'
        )

    def get_is_subscribed(self, obj):
        if self.context['request'].user.is_authenticated:
            return Follow.objects.filter(
                author=obj,
                user=self.context['request'].user
            ).exists()
        return False


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для ингредиентов"""
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для тэгов"""
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class RecipeIngredientsSerializer(serializers.ModelSerializer):
    """Сериализатор для промежуточной модели, свзявающей рецепт
    и ингедиенты"""
    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.StringRelatedField(source='ingredient.name')
    measurement_unit = serializers.StringRelatedField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для получения рецептов"""
    tags = TagSerializer(read_only=True, many=True)
    ingredients = RecipeIngredientsSerializer(
        read_only=True,
        many=True,
        source='recipes_ingredients'
    )
    author = CustomUserSerializer(read_only=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time'
        )

    def get_is_favorited(self, obj):
        if self.context['request'].user.is_authenticated:
            return Favorite.objects.filter(
                user=self.context['request'].user,
                recipe=obj
            ).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        if self.context['request'].user.is_authenticated:
            return ShoppingList.objects.filter(
                user=self.context['request'].user,
                recipe=obj
            ).exists()
        return False


class IngredientForRecipeCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для поля ингредиенты для сериализатора для
    создания рецептов"""
    id = serializers.IntegerField()

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount',)


class RecipeCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания рецептов"""
    ingredients = IngredientForRecipeCreateSerializer(many=True)
    author = CustomUserSerializer(read_only=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'ingredients',
            'tags',
            'name',
            'text',
            'cooking_time',
            'author',
            'image'
        )
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=Recipe.objects.all(),
                fields=('name', 'text'),
                message='Такой рецепт уже существует'
            )
        ]

    def validate(self, data):
        tags = data['tags']
        ingredients = data['ingredients']
        double_checker([tags, ingredients])
        return data

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        ingredient_for_recipe_create(ingredients, recipe)
        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        instance.tags.set(tags)
        RecipeIngredient.objects.filter(recipe=instance.pk).delete()
        ingredient_for_recipe_create(ingredients, instance)
        return super().update(instance, validated_data)

    def to_representation(self, value):
        serializer = RecipeSerializer(value, context=self.context)
        return serializer.data


class RecipeForFavoriteSubscriptionsSerializer(serializers.ModelSerializer):
    """Вложенный сериализатор для сериализаторов для избранного
    и подписок"""
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscriptionsSerializer(CustomUserSerializer):
    """Сериализатор для подписок"""
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count'
        )

    def get_recipes(self, obj):
        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
        queryset = Recipe.objects.filter(author=obj.author)
        if limit:
            queryset = queryset[:int(limit)]
        return RecipeForFavoriteSubscriptionsSerializer(queryset, many=True).data

    def get_recipes_count(self, obj):
        return obj.recipes.all().count()
