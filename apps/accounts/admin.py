from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_validated', 'is_active')
    list_filter = ('role', 'is_validated', 'is_active', 'is_staff')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'phone')
    fieldsets = BaseUserAdmin.fieldsets + (
        ('SAV Info', {
            'fields': ('role', 'phone', 'phone2', 'avatar', 'is_validated', 'windev_user_id'),
        }),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('SAV Info', {
            'fields': ('role', 'phone', 'is_validated'),
        }),
    )
