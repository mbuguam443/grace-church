import mimetypes
import os
import re
from datetime import date

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, HttpResponseNotFound, StreamingHttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.views import View
from django.views.generic import DetailView, ListView, TemplateView

from communication.models import Announcement
from core.models import ChurchSetting
from events.models import Event, EventRegistration
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
        context['gracechurch_audio'] = os.path.isfile(
            os.path.join(settings.STATICFILES_DIRS[0], 'audio', 'gracechurchaudio.mp3')
        )

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


class PublicEventDetailView(DetailView):
    model = Event
    template_name = 'public/event_detail.html'
    context_object_name = 'event'

    def get_queryset(self):
        return Event.objects.filter(is_active=True)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        user = self.request.user
        if user.is_authenticated:
            profile = getattr(user, 'member_profile', None)
            ctx['is_registered'] = bool(
                profile and self.get_object().registrations.filter(member=profile).exists()
            ) or self.get_object().registrations.filter(user=user).exists()
        else:
            ctx['is_registered'] = False
        return ctx


class PublicEventRegisterView(LoginRequiredMixin, View):
    def post(self, request, pk):
        event = get_object_or_404(Event.objects.filter(is_active=True), pk=pk)

        if event.date < date.today():
            messages.error(request, 'This event has already taken place.')
            return redirect('public:event-detail', pk=event.pk)

        if event.is_full:
            messages.error(request, 'This event is already at full capacity.')
            return redirect('public:event-detail', pk=event.pk)

        profile = getattr(request.user, 'member_profile', None)
        if profile is not None:
            registration, created = EventRegistration.objects.get_or_create(
                event=event,
                member=profile,
            )
        else:
            registration, created = EventRegistration.objects.get_or_create(
                event=event,
                user=request.user,
            )

        if created:
            messages.success(request, 'You have been registered for this event. See you there!')
        else:
            messages.info(request, 'You are already registered for this event.')

        return redirect('public:event-detail', pk=event.pk)


class PublicSermonsView(ListView):
    model = Sermon
    template_name = 'public/sermons.html'
    context_object_name = 'sermons'
    paginate_by = 9

    def get_queryset(self):
        queryset = super().get_queryset()
        q = self.request.GET.get('q', '')
        category = self.request.GET.get('category', '')
        series = self.request.GET.get('series', '')
        speaker = self.request.GET.get('speaker', '')
        if q:
            from django.db.models import Q
            queryset = queryset.filter(
                Q(title__icontains=q)
                | Q(speaker__icontains=q)
                | Q(bible_verse__icontains=q)
                | Q(description__icontains=q)
            )
        if category:
            queryset = queryset.filter(category__iexact=category)
        if series:
            queryset = queryset.filter(series__iexact=series)
        if speaker:
            queryset = queryset.filter(speaker__iexact=speaker)
        return queryset.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        queryset = self.get_queryset()
        context['latest'] = queryset.first()
        context['series_list'] = (
            Sermon.objects.exclude(series='')
            .values_list('series', flat=True)
            .distinct()
            .order_by('series')
        )
        context['speakers'] = (
            Sermon.objects.exclude(speaker='')
            .values_list('speaker', flat=True)
            .distinct()
            .order_by('speaker')
        )
        context['categories'] = [
            (value, label) for value, label in Sermon.CATEGORY_CHOICES
            if Sermon.objects.filter(category=value).exists()
        ]
        context['q'] = self.request.GET.get('q', '')
        context['category'] = self.request.GET.get('category', '')
        context['series'] = self.request.GET.get('series', '')
        context['speaker'] = self.request.GET.get('speaker', '')
        qs_params = []
        for key in ('q', 'category', 'series', 'speaker'):
            value = self.request.GET.get(key, '')
            if value:
                qs_params.append(f'{key}={value}')
        context['preserved_q'] = ('&'.join(qs_params) + '&') if qs_params else ''
        return context


class PublicSermonDetailView(DetailView):
    model = Sermon
    template_name = 'public/sermon_detail.html'
    context_object_name = 'sermon'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        sermon = self.get_object()
        related = Sermon.objects.exclude(pk=sermon.pk)
        if sermon.series:
            related = related.filter(series=sermon.series)
        ctx['related'] = related.order_by('-date')[:6]
        return ctx


class PublicContactView(TemplateView):
    template_name = 'public/contact.html'


class PublicGiveView(TemplateView):
    template_name = 'public/give.html'


_ALLOWED_AUDIO = {
    'weak-men-vs-distorted-women.mp3',
    'weak-men-vs-distorted-women-full.mp3',
    'gracechurchaudio.mp3',
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


def _resolve_audio(filename):
    base = os.path.basename(filename)
    if base in _ALLOWED_AUDIO:
        return os.path.join(settings.STATICFILES_DIRS[0], 'audio', base)
    try:
        church = ChurchSetting.get_settings()
    except Exception:
        return None
    if church.audio_file and church.audio_basename == base:
        return os.path.join(settings.MEDIA_ROOT, church.audio_file.name)
    return None


def _serve_file(request, filepath, content_type, base):
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
        content_type=content_type,
    )
    resp['Accept-Ranges'] = 'bytes'
    resp['Content-Length'] = str(length)
    resp['Content-Disposition'] = 'inline; filename="%s"' % base
    if has_range:
        resp.status_code = 206
        resp['Content-Range'] = 'bytes %d-%d/%d' % (start, end, size)
    return resp


def stream_audio(request, filename):
    base = os.path.basename(filename)
    filepath = _resolve_audio(base)
    if not filepath or not os.path.isfile(filepath):
        return HttpResponseNotFound('Not found')

    content_type, _ = mimetypes.guess_type(filepath)
    return _serve_file(request, filepath, content_type or 'audio/mpeg', base)


def serve_media(request, filepath):
    """Serve uploaded files from MEDIA_ROOT through Django so /media/ works
    without relying on a public_html symlink in production (DEBUG off)."""
    base = os.path.basename(filepath)
    media_root = os.path.realpath(settings.MEDIA_ROOT)
    full = os.path.realpath(os.path.join(media_root, filepath))
    is_within = os.path.commonpath([media_root, full]) == media_root
    if not is_within or not os.path.isfile(full):
        return HttpResponseNotFound('Not found')

    content_type, _ = mimetypes.guess_type(full)
    return _serve_file(request, full, content_type or 'application/octet-stream', base)
