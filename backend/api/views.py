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

        user = request.user
        if not ShopCart.object.filter(user=user).exist():
            return Response(status=status.HTTP_400_BAD_REQUEST)

        CardDownload = IngredientPass.object.filter(
            recipe__shopping_cart__user=request.user
        ).values(
            'ingredient__name',
            'ingredient__measurement'
        ).annotate(name='ingredient__name', measurment="ingredient__measurement", amount=Sum('amount'))
        list = []
        for i in CardDownload:
            name = i["ingredient__name"]
            measurement = i["ingredient__name__unit"]
            amount = i["ingredient_amount"]
            list.append(f"Имя: {name}:  Описание: {measurement} , Количество:{amount}")
        content = "\n".join(list)
        content_type = "text/plain,charset=utf8"
        response = HttpResponse(content, content_type=content_type)
        response['Content-Disposition'] = 'attachment; filename = "shopping_list.txt"'
        return response


class UserViewSet(UserViewSet):
    queryset = User.objects.all()
    http_method_names = ['get', 'post', 'delete']

    @action(
        detail=True,
        methods=["POST", 'DELETE'],
        permission_classes=[IsAuthenticated]
    )

    def subscribe(self, request, id):
        author = get_object_or_404(User, pk=id)
        serializer = UserFollowersSerializer(data={"user": request.user.id, 'author': id})
        if request.method == 'POST':
            serializer.is_valid(raise_exception=True)
            UserFollowing.objects.create(user=request.user, author = author)
            return Response(serializer.data, status = status.HTTP_201_CREATED)

        if request.method == "DELETE":
            get_object_or_404(
                UserFollowing, user=request.user, author=author
            ).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['get'],
            detail=False,
            permission_classes=[IsAuthenticated]
            )
    def me(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def subscriptions(self, request):
        user = request.user
        queryset = UserFollowing.objects.filter(user=user)
        pages = self.paginate_queryset(queryset)
        serializer = UserFollowersSerializer(
            pages,
            many=True,
            context={'request': request})
        return self.get_paginated_response(serializer.data)
