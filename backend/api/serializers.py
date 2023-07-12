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
    "Сериалайзер для пользователя"
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
        if request.user.is_authenticated:
            return UserFollowing.objects.filter(user=request.user, author=data).exists()
        return False


class TagSerializer(serializers.ModelSerializer):
    "Сериалайзер для тегов"
    class Meta:
        model = Tag
        fields = ["id", 'name', "color", "slug"]
        read_only_fields = ['__all__']


class IngredientSerializer(serializers.ModelSerializer):
    "Сериалайзер для ингредиентов"
    class Meta:
        model = Ingredient
        fields = ["id", "name", "measures"]


class IngredientForSerializer(serializers.ModelSerializer):
    "Сериалайзер для подключение интгредиентов к рецепту"
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all(), source="ingredient.id")
    name = serializers.ReadOnlyField(source="ingredient.name")
    measurement_unit = serializers.ReadOnlyField(source="ingredient.measures")

    class Meta:
        model = IngredientPass
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipesSerializer(serializers.ModelSerializer):
    "Показ рецепта по GET запросу"
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
        if request.user.is_authenticated:
            return Favorite.objects.filter(recipe=obj, user=request.user).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request.user.is_authenticated:
            return ShopCart.objects.filter(recipe=obj, user=request.user).exists()
        return False


class TagWrite(serializers.ModelSerializer):
    "Сериалайзер для подключения тега"
    id = serializers.IntegerField()

    class Meta:
        model = Tag
        fields = ('id')


class SmallRecipeSerializer(serializers.ModelSerializer):
    "Сериалайзер для отображения рецепта"

    class Meta:
        model = Recipes
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = ('id', 'name', 'image', 'cooking_time')


class CreateOrUpdateRecipes(serializers.ModelSerializer):
    "Сериалайзер для создания и обновления рецепта"
    tags = serializers.PrimaryKeyRelatedField(many=True, queryset=Tag.objects.all())
    author = serializers.HiddenField(default=serializers.CurrentUserDefault())
    ingredients = IngredientForSerializer(many=True, write_only=True)
    image = Base64ImageField()

    class Meta:
        model = Recipes
        fields = ('tags', 'author', 'ingredients',
                  'name', 'image', 'text', 'cooking_time')

    def create(self, validated_data):
        print(validated_data)
        ingredients = validated_data.pop('ingredients')
        recipe = super().create(validated_data)

        for ingredient in ingredients:
            IngredientPass.objects.update_or_create(
                recipe=recipe,
                ingredient=ingredient.get("ingredient").get("id"),
                defaults={
                    "amount": ingredient.get("amount", 0)
                }
            )

        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients')
        recipe = super().update(instance, validated_data)

        for ingredient in ingredients:
            IngredientPass.objects.update_or_create(
                recipe=recipe,
                ingredient=ingredient.get("ingredient").get("id"),
                defaults={
                    "amount": ingredient.get("amount", 0)
                }
            )


class RegisterSerializer(UserCreateSerializer):
    "Сериалайзер для регистрации"
    class Meta:
        model = User
        fields = ('email', 'username', 'first_name', 'last_name', 'password')


class UserFollowersSerializer(serializers.ModelSerializer):
    "Сериалайзер для подписки"

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

    def get_recipes_count(self, user_following):
        return user_following.author.recipes.count()


class FavoriteSerializer(serializers.ModelSerializer):
    "Сериалайзер для избранного"
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
