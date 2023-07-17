from django.db.models import Sum
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .filters import RecipeFilter
from .pagination import LimitPageNumberPagination
from recipes.models import Favorite, Ingredient, Recipe, ShopCart, Tag
from users.models import User, UserFollowing
from .serializers import (
    CreateOrUpdateRecipes,
    FollowGetSerializer,
    IngredientSerializer,
    RecipesSerializer,
    TagSerializer,
    UserFollowersSerializer,
    UserSerializer
)
from .utils import add_to, delete_from


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
    permission_classes = (AllowAny,)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    permission_classes = (AllowAny,)


class RecipesViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    http_method_names = ['get', 'post', 'patch', 'create', 'delete']
    filter_backends = (DjangoFilterBackend,)
    pagination_class = LimitPageNumberPagination
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.action == "list" or self.action == "retrieve":
            return RecipesSerializer
        return CreateOrUpdateRecipes

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def favorite(self, request, pk):
        if request.method == 'POST':
            return add_to(Favorite, request, request.user, pk)
        return delete_from(Favorite, request.user, pk, request)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def shopping_cart(self, request, pk):
        if request.method == 'POST':
            return add_to(ShopCart, request, request.user, pk)
        return delete_from(ShopCart, request.user, pk, request)

    @action(
        detail=False,
        methods=['get'],
    )
    def download_shopping_cart(self, request):
        ingredients = Ingredient.objects.filter(
            recipe_pass__recipe__shopping_cart__user=request.user
        ).annotate(
            amount=Sum("recipe_pass__amount")
        ).values_list(
            "name",
            "measures",
            "amount",
        )
        shopping_cart = 'Список покупок:\n'

        for name, measure, amount in ingredients:
            shopping_cart += f'{name.capitalize()} {amount} {measure},\n'
        response = HttpResponse(shopping_cart,
                                content_type='text/plain')
        response['Content-Disposition'] = (
            'attachment; filename=Shopping list.txt'
        )
        return response


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()
    http_method_names = ['get', 'post', 'delete']
    pagination_class = LimitPageNumberPagination
    permission_classes = (AllowAny,)

    @action(
        detail=True,
        methods=["POST", "DELETE"],
        permission_classes=[IsAuthenticated]
    )
    def subscribe(self, request, id):
        author = self.get_object()
        if request.method == "POST":
            user_following, created = UserFollowing.objects.get_or_create(
                author=author,
                user=request.user
            )
            serializer = UserFollowersSerializer(user_following)
            return Response(
                data=serializer.data,
                status=status.HTTP_201_CREATED
            )
        else:
            UserFollowing.objects.filter(
                author=author,
                user=request.user
            ).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=['get'],
        detail=False,
        permission_classes=[IsAuthenticated]
    )
    def me(self, request):
        serializer = UserSerializer(
            request.user, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated],
        pagination_class=LimitPageNumberPagination
    )
    def subscriptions(self, request):
        user = request.user
        queryset = User.objects.filter(subscribing__user=user)
        pages = self.paginate_queryset(queryset)
        serializer = FollowGetSerializer(
            pages, many=True, context={'request': request})
        return self.get_paginated_response(serializer.data)
