from django.contrib import admin
from core.constance import EMPTY_VALUE_DISPLAY
from users.models import User, Follow


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'email', 'first_name', 'last_name')
    list_filter = ('username', 'email')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    empty_value_display = EMPTY_VALUE_DISPLAY


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'author')
    search_fields = ('user__username', 'author__username')
    list_filter = ('user__username', 'author__username')
    empty_value_display = EMPTY_VALUE_DISPLAY
