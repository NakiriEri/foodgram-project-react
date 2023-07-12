from django.contrib import admin

from .models import User, UserFollowing


class UserAdmin(admin.ModelAdmin):
    list_display = (
        'first_name',
        'last_name',
        'username',
        'email',
        'role',
    )

    list_filter = ("username", 'email')
    search_fields = ('username', 'email')


class SubscribeAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'author'
    )
    list_display_links = ('id', 'user')
    search_fields = ('user',)


admin.site.register(User, UserAdmin)
admin.site.register(UserFollowing, SubscribeAdmin)
