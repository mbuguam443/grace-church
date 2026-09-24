from urllib.parse import urlparse

from django.conf import settings
from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from events.models import Event
from sermons.models import Sermon

_parsed = urlparse(getattr(settings, 'SITE_URL', '') or '')
_PROTOCOL = _parsed.scheme or 'https'
_DOMAIN = _parsed.netloc or 'localhost'


class _BaseSitemap(Sitemap):
    protocol = _PROTOCOL

    def get_domain(self, site=None):
        return _DOMAIN


class StaticViewSitemap(_BaseSitemap):
    _pages = {
        'public:home': (1.0, 'weekly'),
        'public:sermons': (0.9, 'daily'),
        'public:events': (0.8, 'daily'),
        'public:about': (0.7, 'monthly'),
        'public:ministries': (0.7, 'monthly'),
        'public:services': (0.7, 'weekly'),
        'public:contact': (0.6, 'monthly'),
        'public:give': (0.6, 'monthly'),
    }

    def items(self):
        return list(self._pages.keys())

    def location(self, item):
        return reverse(item)

    def priority(self, item):
        return self._pages[item][0]

    def changefreq(self, item):
        return self._pages[item][1]


class SermonSitemap(_BaseSitemap):
    priority = 0.8
    changefreq = 'monthly'

    def items(self):
        return Sermon.objects.all()

    def lastmod(self, obj):
        return obj.updated_at or obj.created_at

    def location(self, obj):
        return reverse('public:sermon-detail', args=[obj.pk])


class EventSitemap(_BaseSitemap):
    priority = 0.7
    changefreq = 'weekly'

    def items(self):
        return Event.objects.filter(is_active=True)

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return reverse('public:event-detail', args=[obj.pk])


sitemaps = {
    'static': StaticViewSitemap,
    'sermons': SermonSitemap,
    'events': EventSitemap,
}
