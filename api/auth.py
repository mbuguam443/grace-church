import functools

from django.http import JsonResponse

from .models import ApiToken


def token_required(view_func):
    @functools.wraps(view_func)
    def wrapper(request, *args, **kwargs):
        auth_header = request.headers.get('Authorization', '')
        key = ''
        if auth_header.startswith('Token '):
            key = auth_header[6:].strip()
        if not key:
            key = request.GET.get('token', '') or request.POST.get('token', '')
        if not key:
            return JsonResponse({'error': 'Authentication required'}, status=401)
        try:
            token = ApiToken.objects.select_related('user').get(key=key)
        except ApiToken.DoesNotExist:
            return JsonResponse({'error': 'Invalid or expired token'}, status=401)
        request.user = token.user
        request.api_token = token
        return view_func(request, *args, **kwargs)
    return wrapper


def get_member(user):
    profile = getattr(user, 'member_profile', None)
    if profile is not None:
        return profile
    return None