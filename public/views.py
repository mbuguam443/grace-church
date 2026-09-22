import os
import re
from datetime import date

from django.conf import settings
from django.http import HttpResponse, HttpResponseNotFound, StreamingHttpResponse
from django.views.generic import ListView, TemplateView

from communication.models import Announcement
from events.models import Event
from ministries.models import Ministry
from sermons.models import Sermon
from services.models import Service


class PublicHomeView(TemplateView):
    template_name = 'public/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = date.today()

        context['upcoming_events'] = Event.objects.filter(
            date__gte=today,
            is_active=True
        ).order_by('date', 'time')[:5]

        context['latest_sermons'] = Sermon.objects.all()[:5]
        context['ministries'] = Ministry.objects.filter(is_active=True)
        context['service_times'] = Service.objects.filter(
            date__gte=today
        ).order_by('date', 'start_time')[:3]
        context['announcements'] = Announcement.objects.filter(
            is_active=True
        ).order_by('-created_at')[:5]

        return context


class PublicAboutView(TemplateView):
    template_name = 'public/about.html'


class PublicMinistriesView(ListView):
    model = Ministry
    template_name = 'public/ministries.html'
    context_object_name = 'ministries'

    def get_queryset(self):
        return Ministry.objects.filter(is_active=True)


class PublicServicesView(ListView):
    model = Service
    template_name = 'public/services.html'
    context_object_name = 'services'

    def get_queryset(self):
        return Service.objects.filter(
            date__gte=date.today()
        ).order_by('date', 'start_time')


class PublicEventsView(ListView):
    model = Event
    template_name = 'public/events.html'
    context_object_name = 'events'

    def get_queryset(self):
        return Event.objects.filter(
            date__gte=date.today(),
            is_active=True
        ).order_by('date', 'time')


class PublicSermonsView(ListView):
    model = Sermon
    template_name = 'public/sermons.html'
    context_object_name = 'sermons'
    paginate_by = 10


class PublicContactView(TemplateView):
    template_name = 'public/contact.html'


class PublicGiveView(TemplateView):
    template_name = 'public/give.html'


_ALLOWED_AUDIO = {
    'weak-men-vs-distorted-women.mp3',
    'weak-men-vs-distorted-women-full.mp3',
}
_CHUNK = 262144


def _range_chunks(filepath, start, end):
    remaining = end - start + 1
    with open(filepath, 'rb') as f:
        f.seek(start)
        while remaining > 0:
            data = f.read(min(_CHUNK, remaining))
            if not data:
                break
            remaining -= len(data)
            yield data


def stream_audio(request, filename):
    if filename not in _ALLOWED_AUDIO or not filename.endswith('.mp3'):
        return HttpResponseNotFound('Not found')
    filepath = os.path.join(settings.STATICFILES_DIRS[0], 'audio', filename)
    if not os.path.isfile(filepath):
        return HttpResponseNotFound('Not found')

    size = os.path.getsize(filepath)
    start, end = 0, size - 1
    has_range = False

    match = re.match(r'bytes=(\d*)-(\d*)', request.headers.get('Range', ''))
    if match:
        has_range = True
        start_spec = match.group(1)
        end_spec = match.group(2)
        if start_spec:
            start = int(start_spec)
            end = int(end_spec) if end_spec else size - 1
        else:
            start = max(0, size - int(end_spec or '0'))
            end = size - 1
        if start >= size:
            resp = HttpResponse(status=416)
            resp['Content-Range'] = 'bytes */%d' % size
            return resp

    length = end - start + 1
    resp = StreamingHttpResponse(
        _range_chunks(filepath, start, end),
        content_type='audio/mpeg',
    )
    resp['Accept-Ranges'] = 'bytes'
    resp['Content-Length'] = str(length)
    resp['Content-Disposition'] = 'inline; filename="%s"' % filename
    if has_range:
        resp.status_code = 206
        resp['Content-Range'] = 'bytes %d-%d/%d' % (start, end, size)
    return resp
