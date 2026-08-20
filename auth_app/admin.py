from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


class CustomUserAdmin(UserAdmin):
    """Configure the custom user model for the Django admin."""

    ordering = ("email",)


admin.site.register(User, CustomUserAdmin)
