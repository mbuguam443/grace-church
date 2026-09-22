from datetime import date

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
