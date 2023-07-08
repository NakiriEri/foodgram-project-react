from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django_filters.rest_framework import DjangoFilterBackend
from django.http import HttpResponse

from djoser.views import UserViewSet
from recipes.models import Tag, Recipes, Ingredient, ShopCart, Favorite, IngredientPass
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from users.models import UserFollowing

from .serializers import (UserSerializer, TagSerializer, RecipesSerializer, IngredientSerializer,
                          UserFollowersSerializer, SmallRecipeSerializer, CreateOrUpdateRecipes)
from .utils import add_to, delete_from

User = get_user_model()


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
    permission_classes = (AllowAny,)


class IngridientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    permission_classes = (AllowAny,)


class RecipesViewSet(viewsets.ModelViewSet):
    queryset = Recipes.objects.all()
    http_method_names = ['get', 'post', 'patch', 'create', 'delete']
    filter_backends = (DjangoFilterBackend, )


    def get_serializer_class(self):
        if self.request.method == "GET":
            return RecipesSerializer
        else:
            return CreateOrUpdateRecipes



    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated])
    def favorite(self, request, pk):

        if request.method == 'POST':
            return add_to(model = Favorite, user = request.user, pk=pk, request = request)
        if request.method == "DELETE":
            return delete_from(model = Favorite, user = request.user, pk=pk, request = request)
    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def shopping_cart(self, request, pk):
        if request.method == 'POST':
            return add_to(model = Favorite, user = request.user, pk=pk, request = request)
        if request.method == "DELETE":
            return delete_from(model = Favorite, user = request.user, pk=pk, request = request)

    @action(
        detail=False,
        methods=['get'],
    )
    def download_shopping_cart(self, request):

        pass


class UserViewSet(UserViewSet):
    queryset = User.objects.all()
    http_method_names = ['get', 'post', 'delete']

    @action(
        detail=True,
        methods=["POST", 'DELETE'],
        permission_classes=[IsAuthenticated]
    )

    def subscribe(self, request, id):
        pass

    @action(methods=['get'],
            detail=False,
            permission_classes=[IsAuthenticated]
            )
    def me(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def subscriptions(self, request):
        pass
