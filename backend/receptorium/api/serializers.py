from django.shortcuts import get_object_or_404
from djoser.serializers import UserSerializer
from drf_extra_fields.fields import Base64ImageField
from recipes.models import (Favorite, Follow, Ingredient, Recipe,
                            RecipeIngredient, ShoppingList, Tag)
from rest_framework import serializers
from user.models import User


class CustomUserSerializer(UserSerializer):
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
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class RecipeIngredientsSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.StringRelatedField(source='ingredient.name')
    measurement_unit = serializers.StringRelatedField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
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
    id = serializers.IntegerField()

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount',)


class RecipeCreateSerializer(serializers.ModelSerializer):
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

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        for ingredient in ingredients:
            current_ingredient = get_object_or_404(
                Ingredient,
                id=ingredient['id']
            )
            RecipeIngredient.objects.create(
                ingredient=current_ingredient,
                recipe=recipe,
                amount=ingredient['amount']
            )
        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        instance.tags.set(tags)
        RecipeIngredient.objects.filter(recipe=instance.pk).delete()
        for ingredient in ingredients:
            current_ingredient = get_object_or_404(
                Ingredient,
                id=ingredient['id']
            )
            RecipeIngredient.objects.create(
                ingredient=current_ingredient,
                recipe=instance,
                amount=ingredient['amount']
            )
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time
        )
        instance.author = validated_data.get('author', instance.author)
        instance.image = validated_data.get('image', instance.image)
        instance.save()
        return instance

    def to_representation(self, value):
        serializer = RecipeSerializer(value, context=self.context)
        return serializer.data


class RecipeForFavoriteSubscriptionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscriptionsSerializer(CustomUserSerializer):
    recipes = RecipeForFavoriteSubscriptionsSerializer(many=True)
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

    def get_recipes_count(self, obj):
        return obj.recipes.all().count()
