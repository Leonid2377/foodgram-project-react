from django.contrib.auth import get_user_model
from rest_framework import serializers
from djoser.serializers import UserCreateSerializer, UserSerializer
from foodgram.models import Tag, Ingredient, ShoppingList, Recipe, Subscription, FavoriteList
from rest_framework.validators import UniqueTogetherValidator

from users.model import Follow


User = get_user_model()


class CustomUserCreateSerializer(UserCreateSerializer):
    class Meta:
        model = User
        fields = ('email', 'username', 'first_name', 'last_name', 'password')


class CustomUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name',
            'last_name', 'is_subscribed'
        )

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request.user.is_authenticated:
            return Follow.objects.filter(user=request.user,
                                         following=obj).exists()


class FollowRecipesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class FollowListSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField(read_only=True)
    recipes = serializers.SerializerMethodField(read_only=True)
    recipes_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count')

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request.user.is_authenticated:
            return Follow.objects.filter(user=request.user,
                                         following=obj).exists()

    def get_recipes(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        context = {'request': request}
        recipes_limit = request.query_params.get('recipes_limit')
        if recipes_limit is not None:
            recipes = obj.recipes.all()[:int(recipes_limit)]
        else:
            recipes = obj.recipes.all()
        return FollowRecipesSerializer(
            recipes, many=True, context=context).data

    def get_recipes_count(self, obj):
        return obj.recipes.count()


class UserFollowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Follow
        fields = ('user', 'following')
        validators = [
            UniqueTogetherValidator(
                queryset=Follow.objects.all(),
                fields=('user', 'following'),
                message=('Вы уже подписаны на этого пользователя')
            )
        ]

    def validate(self, data):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        following = data['following']
        if request.user == following:
            raise serializers.ValidationError(
                'Вы не можете подписаться на себя!'
            )
        return data

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return FollowListSerializer(
            instance.following, context=context).data


class TagSerializer(serializers.ModelSerializer):  # OK
    class Meta:
        fields = ('id', 'title', 'color', 'slug')
        model = Tag


class IngredientSerializer(serializers.ModelSerializer):  # OK
    class Meta:
        fields = ('id', 'title', 'measurement_unit')
        model = Ingredient


class RecipeRepresentationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class FavoriteRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = FavoriteList
        fields = ('user', 'recipe')

    def validate(self, data):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        recipe = data['recipe']
        if FavoriteList.objects.filter(
            user=request.user,
            recipe=recipe
        ).exists():
            raise serializers.ValidationError({
                'recipe': 'Этот рецепт уже есть в избранном'
            })
        return data

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return RecipeRepresentationSerializer(
            instance.recipe, context=context).data


class ShoppingListSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShoppingList
        fields = ('user', 'recipe')

    def validate(self, data):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        recipe = data['recipe']
        if ShoppingList.objects.filter(
            user=request.user,
            recipe=recipe
        ).exists():
            raise serializers.ValidationError({
                'recipe': 'Этот рецепт уже есть в корзине'
            })
        return data

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return RecipeRepresentationSerializer(
            instance.recipe, context=context).data



