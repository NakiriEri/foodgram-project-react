from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework import filters, status, viewsets
from recipes.models import Tag, Recipes, Ingredient, Favorite
from .serializers import (UserSerializer, RegisterSerializer, TagSerializer, RecipesSerializer, IngredientSerializer,
                          CreateOrUpdateRecipes, SmallRecipeSerializer, UserFollowersSerializer, FavoriteSerializer)
def add_to(model, request, user, pk):
    if model.objects.filter(user=user).exists():
        return Response({'error': 'Уже существует'},
                        status=status.HTTP_400_BAD_REQUEST)
    recipe = get_object_or_404(Recipes, id=pk)
    model.objects.create(user=user, recipe=recipe)
    serializer = SmallRecipeSerializer(instance=recipe, context={'request': request})
    return Response(data=serializer.data, status=status.HTTP_201_CREATED)

def delete_from(model, user, pk, request):
    recipe = get_object_or_404(Recipes, id=pk)
    if  model.objects.filter(user=user, recipe=recipe).exists():
        model.objects.filter(
            user=user, recipe=recipe
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    return Response(status=status.HTTP_400_BAD_REQUEST)
