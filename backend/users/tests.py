from django.test import TestCase

# Create your tests here.
@action(detail=True, methods=['post'], url_path='favorite')
def add_to_favorites(self, request, pk=None):
    if not request.user.is_authenticated:
        return Response(
            {'detail': 'Пользователь не авторизован'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    recipe = self.get_object()
    user = request.user
    favorite, created = Favorite.objects.get_or_create(user=user)
    favorite.recipes.add(recipe)
    return Response(
        {'detail': 'Рецепт успешно добавлен в избранное'},
        status=status.HTTP_200_OK
    )


@action(detail=True, methods=['delete'], url_path='favorite')
def remove_from_favorites(self, request, pk=None):
    recipe = self.get_object()
    user = request.user
    favorites = Favorite.objects.filter(user=user, recipes=recipe)
    if favorites.exists():
        favorites.delete()
        return Response(
            {'detail': 'Рецепт успешно удален из избранного'},
            status=status.HTTP_200_OK
        )
    return Response(
        {'detail': 'Ошибка удаления'},
        status=status.HTTP_400_BAD_REQUEST
    )