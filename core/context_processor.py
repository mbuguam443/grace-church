from django.conf import settings
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


def seo_defaults(request):
    import json

    site_url = getattr(settings, 'SITE_URL', '').rstrip('/')
    try:
        church = ChurchSetting.get_settings()
    except Exception:
        church = None

    org = {
        '@context': 'https://schema.org',
        '@type': 'Church',
        'name': (church.church_name if church else '') or 'Grace Church Munyaka',
        'url': site_url or '',
    }
    if church:
        if church.logo:
            org['logo'] = site_url + church.logo.url
        if church.email:
            org['email'] = church.email
        if church.phone:
            org['telephone'] = church.phone
        if church.address:
            org['address'] = {
                '@type': 'PostalAddress',
                'streetAddress': church.address,
            }
        if church.website:
            org['sameAs'] = [church.website]

    return {
        'site_url': site_url,
        'default_meta_description': getattr(settings, 'DEFAULT_META_DESCRIPTION', ''),
        'organization_jsonld': json.dumps(org, ensure_ascii=False),
    }


# Which module keys each sidebar section needs before its heading is shown.
SIDEBAR_SECTIONS = {
    'management': ['members', 'families', 'visitors', 'services', 'attendance', 'ministries', 'groups', 'children'],
    'church_life': ['events', 'sermons', 'ministries', 'songs', 'bible_study', 'sunday_school', 'announcements'],
    'finance': ['finance', 'giving'],
    'operations': ['assets', 'facilities', 'reports'],
    'administration': ['users', 'settings'],
}


def module_permissions(request):
    allowed = None
    if request.user.is_authenticated:
        allowed = RoleModulePermission.allowed_modules_for(request.user.role)
    sections = {
        name: allowed is None or any(key in allowed for key in keys)
        for name, keys in SIDEBAR_SECTIONS.items()
    }
    return {
        'allowed_modules': allowed,
        'sidebar_sections': sections,
    }


def pending_registrations(request):
    User = get_user_model()
    count = 0
    if request.user.is_authenticated and request.user.is_admin_user:
        count = User.objects.filter(is_active=False, role='member').count()
    return {
        'pending_registrations_count': count,
    }