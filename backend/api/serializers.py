import re
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer, SerializerMethodField, ReadOnlyField
from drf_extra_fields.fields import Base64ImageField
from djoser.serializers import UserCreateSerializer

from recipes.models import Tag, Recipes, Ingredient, IngredientPass, Favorite, ShopCart
from users.models import UserFollowing

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = SerializerMethodField(read_only=True)

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

    def validate_username(self, value):
        if value == 'me':
            raise serializers.ValidationError(
                {
                    'username':
                        'Нельзя использовать me в качестве имени пользователя.'
                }
            )
        match = re.fullmatch(r'^[\w.@+-]+', str(value))
        if match is None:
            raise serializers.ValidationError('Недоспустимые символы')
        return value

    def get_is_subscribed(self, data):
        request = self.context.get('request')
        return UserFollowing.objects.filter(user=request.user, author=data).exists()


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ["id", 'name', "color", "slug"]
        read_only_fields = ['__all__']


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ["id", "name", "measures"]


class IngredientForSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source="ingredient.id")
    name = serializers.ReadOnlyField(source="ingredient.name")
    measurement_unit = serializers.ReadOnlyField(source="ingredient.measures")

    class Meta:
        model = IngredientPass
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipesSerializer(serializers.ModelSerializer):
    tags = TagSerializer(read_only=True, many=True)
    author = UserSerializer(read_only=True)
    ingredients = IngredientForSerializer(many=True,
                                          read_only=True, source="recipe_pass")
    image = Base64ImageField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()

    class Meta:
        model = Recipes
        fields = ("id", "tags", "author", "ingredients", "is_favorited", "is_in_shopping_cart", "name", "image", "text",
                  "cooking_time")
        read_only_fields = ['is_favorited', "is_in_shopping_cart"]

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        return Favorite.objects.filter(recipe=obj, user=request.user).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        return ShopCart.objects.filter(recipe=obj, user=request.user).exists()

class TagWrite(serializers.ModelSerializer):
    id = serializers.IntegerField()

    class Meta:
        model = Tag
        fields = ('id')


class SmallRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipes
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = ('id', 'name', 'image', 'cooking_time')


class CreateOrUpdateRecipes(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(many = True, queryset = Tag.objects.all())
    author = UserSerializer(read_only=True)
    ingredients = IngredientForSerializer(many=True)
    image = Base64ImageField()


    class Meta:
        model = Recipes
        fields = ('tags', 'author', 'ingredients',
                  'name', 'image', 'text', 'cooking_time')


    def create_ingredients(self, recipes, ingredients):
        for ingredient in ingredients:
            IngredientPass.object.creare(id=Ingredient.objects.get(ingredient("id")),
                                         recipes=recipes,
                                         amount=ingredient.get("amount"),
                                         ingredient=ingredient.get("id")
                                         )



class RegisterSerializer(UserCreateSerializer):
    class Meta:
        model = User
        fields = ('email', 'username', 'first_name', 'last_name', 'password')


class UserFollowersSerializer(serializers.ModelSerializer):
    recipes_count = SerializerMethodField()

    class Meta:
        model = UserFollowing
        fields = ("author", "user", 'recipes_count',)

    def validate(self, data):
        author = self.instance
        users = get_object_or_404(User, email=data.get('user'))

        if User.objects.filter(email=author).exist() != True:
            raise serializers.ValidationError("Данного пользователя не удалось найти")
        if author == users:
            raise serializers.ValidationError("Вы пытаетесь подписаться на самого себя")
        if User.objects.filter(user=users, author=author).exist() == True:
            raise serializers.ValidationError("Вы уже подписаны на данного пользователя")

        return data

    def get_recipes_count(self, author):
        return author.recipes.count()


class FavoriteSerializer(serializers.ModelSerializer):
    name = serializers.ReadOnlyField(
        source='recipes.name',
        read_only=True)
    image = serializers.ImageField(
        source='recipes.image',
        read_only=True)
    cooking_time = serializers.IntegerField(
        source='recipes.cooking_time',
        read_only=True)
    id = serializers.PrimaryKeyRelatedField(
        source='recipes',
        read_only=True)

    class Meta:
        model = Favorite
        fields = ('id', 'name', 'image', 'cooking_time')
