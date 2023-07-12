from django.contrib import admin

from .models import Recipes, Ingredient, Tag, User, IngredientPass, TagPass, Favorite, ShopCart
from users.models import UserFollowing


class TagPassAdmin(admin.TabularInline):
    model = TagPass


class IngredientPassAdmin(admin.TabularInline):
    model = IngredientPass


class RecipesAdmin(admin.ModelAdmin):
    list_display = ('name', 'author')
    list_filter = ('name', 'author', 'tags')
    inlines = (
        TagPassAdmin,
        IngredientPassAdmin
    )

    @admin.display(description='В избранном')
    def get_favorite_count(self, obj):
        return Favorite.objects.filter(recipe=obj).count()


class IngredientAdmin(admin.ModelAdmin):

    list_display = ('name', 'measures',)
    list_filter = ('name',)


class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'slug',)

class SubscribeAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'author'
    )
    list_display_links = ('id', 'user')
    search_fields = ('user',)

@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'recipe'
    )
@admin.register(ShopCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'recipe'
    )

admin.site.register(Recipes, RecipesAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(UserFollowing, SubscribeAdmin)
