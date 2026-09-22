from django.contrib import admin

from .models import ChurchSetting, RoleModulePermission


@admin.register(ChurchSetting)
class ChurchSettingAdmin(admin.ModelAdmin):
    list_display = ('church_name', 'email', 'phone', 'updated_at')


@admin.register(RoleModulePermission)
class RoleModulePermissionAdmin(admin.ModelAdmin):
    list_display = ('role', 'module')
    list_filter = ('role',)
    search_fields = ('role', 'module')