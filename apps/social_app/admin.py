from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from apps.social_app.models import Post, User


@admin.register(Post)
class CustomPostAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'user', 'created_at',)
    search_fields = ('id', 'title',)
    ordering = ('-created_at',)


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('id', 'username', 'email', 'is_staff', 'is_active',)
    search_fields = ('id', 'username', 'email',)
    ordering = ('id',)
