from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework import status
from recipes.models import Recipes
from .serializers import SmallRecipeSerializer


def add_to(model, request, user, pk):
    if model.objects.filter(user=user).exists():
        return Response({'Невозможно добавить, уже существует данная единица'},
                        status=status.HTTP_400_BAD_REQUEST)

    recipe = get_object_or_404(Recipes, id=pk)
    instance = model.objects.create(user=user, recipe=recipe)
    serializer = SmallRecipeSerializer(instance=recipe, context={'request': request})

    return Response(serializer.data, status=status.HTTP_201_CREATED)


def delete_from(model, user, pk, request):
    recipe = get_object_or_404(Recipes, id=pk)

    if model.objects.filter(user=user, recipe=recipe).exists():
        model.objects.filter(
            user=user, recipe=recipe
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    return Response(status=status.HTTP_400_BAD_REQUEST)
