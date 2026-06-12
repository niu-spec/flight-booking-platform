from django.contrib import admin
from apps.user.models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ['username', 'phone', 'email', 'is_active', 'is_staff', 'date_joined']
    list_filter = ['is_active', 'is_staff', 'is_superuser']
    search_fields = ['username', 'phone', 'email']
    ordering = ['-date_joined']
    
    fieldsets = (
        ('基本信息', {'fields': ('username', 'phone', 'email', 'first_name', 'last_name')}),
        ('权限', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('重要日期', {'fields': ('last_login', 'date_joined')}),
    )
