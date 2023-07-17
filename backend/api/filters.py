from django.contrib.auth import get_user_model
from django_filters.rest_framework import FilterSet, filters
from recipes.models import Ingredient, Recipe, Tag


class RecipeFilter(FilterSet):
    tags = filters.ModelMultipleChoiceFilter(
        queryset=Tag.objects.all(),
        field_name='tags__slug',
        to_field_name='slug',
    )

    is_favorited = filters.BooleanFilter(method='filter_is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_is_in_shopping_cart')
    created = filters.DateFilter(field_name='created', lookup_expr='gte')

    class Meta:
        model = Recipe
        fields = ('tags', 'author','created')

    def filter_is_favorited(self, queryset, name, value):
        if value:
            return queryset.filter(favorite__user=self.request.user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        user = self.request.user
        if value:
            return queryset.filter(shopping_cart__user=self.request.user)
        return queryset


class IngredientFilter(FilterSet):
    name = filters.CharFilter(field_name='name', lookup_expr='icontains')


    class Meta:
        model = Ingredient
        fields = ('name',)
