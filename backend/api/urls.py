from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views


router = DefaultRouter()

router.register(r'users', views.UserViewSet, basename='user')
router.register(r'tags', views.TagViewSet, basename='tags')
router.register(r'ingredients', views.IngridientViewSet, basename='ingredients')
router.register(r'recipes', views.RecipesViewSet, basename='recipes')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
]