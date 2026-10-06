from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse


class SponsorAccessMiddleware:
    """Keep sponsor accounts on the dashboard and the outreach records."""

    ALLOWED_EXACT = {'/'}
    ALLOWED_PREFIXES = (
        '/dashboard/',
        '/impact/',
        '/accounts/login/',
        '/accounts/logout/',
        '/accounts/profile/',
        '/accounts/password',
        '/about-us/',
        '/our-ministries/',
        '/service-times/',
        '/upcoming-events/',
        '/our-sermons/',
        '/watch/',
        '/contact-us/',
        '/give-now/',
        '/static/',
        '/media/',
        '/audio/',
        '/robots.txt',
        '/sitemap.xml',
        '/image-test/',
    )

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = getattr(request, 'user', None)
        if user is not None and user.is_authenticated and user.is_sponsor:
            path = request.path
            allowed = path in self.ALLOWED_EXACT or path.startswith(self.ALLOWED_PREFIXES)
            if not allowed:
                messages.error(
                    request,
                    'Your sponsor account only has access to the outreach information.',
                )
                return HttpResponseRedirect(reverse('dashboard:index'))
        return self.get_response(request)
