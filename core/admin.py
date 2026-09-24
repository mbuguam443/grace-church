from django.contrib import admin

from .models import ChurchSetting, Leader, RoleModulePermission


@admin.register(ChurchSetting)
class ChurchSettingAdmin(admin.ModelAdmin):
    list_display = ('church_name', 'email', 'phone', 'updated_at')


@admin.register(RoleModulePermission)
class RoleModulePermissionAdmin(admin.ModelAdmin):
    list_display = ('role', 'module')
    list_filter = ('role',)
    search_fields = ('role', 'module')


@admin.register(Leader)
class LeaderAdmin(admin.ModelAdmin):
    list_display = ('name', 'role', 'order', 'is_active')
    list_editable = ('role', 'order', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'role')