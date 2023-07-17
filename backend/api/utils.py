from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response

from recipes.models import Recipe
from .serializers import SmallRecipeSerializer


def add_to(model, request, user, pk):
    if model.objects.filter(user=user, id = pk).exists():
        return Response({'Невозможно добавить, уже существует данная единица'},
                        status=status.HTTP_400_BAD_REQUEST)
    recipe = get_object_or_404(Recipe, id=pk)
    instance = model.objects.create(user=user, recipe=recipe)
    serializer = SmallRecipeSerializer(recipe)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


def delete_from(model, user, pk, request):
    recipe = get_object_or_404(Recipe, id=pk)
    if model.objects.filter(user=user, recipe=recipe).exists():
        model.objects.filter(
            user=user, recipe=recipe
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    return Response(status=status.HTTP_400_BAD_REQUEST)
