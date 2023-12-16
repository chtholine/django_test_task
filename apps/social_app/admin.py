from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from apps.social_app.models import Post, User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('id', 'username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active',)
    search_fields = ('username', 'email', 'first_name', 'last_name',)
    ordering = ('id',)


admin.site.register(Post)
