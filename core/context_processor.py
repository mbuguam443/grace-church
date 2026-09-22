from django.contrib.auth import get_user_model

from .models import ChurchSetting, RoleModulePermission


def church_settings(request):
    try:
        settings = ChurchSetting.get_settings()
    except Exception:
        settings = None
    return {
        'church_settings': settings,
    }


def module_permissions(request):
    allowed = None
    if request.user.is_authenticated:
        allowed = RoleModulePermission.allowed_modules_for(request.user.role)
    return {
        'allowed_modules': allowed,
    }


def pending_registrations(request):
    User = get_user_model()
    count = 0
    if request.user.is_authenticated and request.user.is_admin_user:
        count = User.objects.filter(is_active=False, role='member').count()
    return {
        'pending_registrations_count': count,
    }