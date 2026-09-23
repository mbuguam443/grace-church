from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, View

from accounts.views import ContentWriteMixin
from members.models import Member
from .models import Event, EventRegistration


class EventListView(LoginRequiredMixin, ListView):
    model = Event
    template_name = 'events/event_list.html'
    context_object_name = 'events'


class EventDetailView(LoginRequiredMixin, DetailView):
    model = Event
    template_name = 'events/event_detail.html'
    context_object_name = 'event'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        event = ctx['event']
        registered_ids = list(event.registrations.values_list('member_id', flat=True))
        ctx['registerable_members'] = Member.objects.filter(
            membership_status='active'
        ).exclude(id__in=registered_ids).order_by('first_name', 'last_name')
        self_member = getattr(self.request.user, 'member_profile', None)
        ctx['self_member'] = self_member
        ctx['self_registered'] = bool(self_member and self_member.id in registered_ids)
        return ctx


class EventCreateView(LoginRequiredMixin, ContentWriteMixin, CreateView):
    model = Event
    template_name = 'events/event_form.html'
    fields = ['name', 'image', 'description', 'date', 'time', 'end_date', 'location', 'organizer', 'speaker', 'capacity', 'registration_required', 'is_active']
    success_url = reverse_lazy('events:event-list')

    def form_valid(self, form):
        messages.success(self.request, 'Event created successfully.')
        return super().form_valid(form)


class EventUpdateView(LoginRequiredMixin, ContentWriteMixin, UpdateView):
    model = Event
    template_name = 'events/event_form.html'
    fields = ['name', 'image', 'description', 'date', 'time', 'end_date', 'location', 'organizer', 'speaker', 'capacity', 'registration_required', 'is_active']
    success_url = reverse_lazy('events:event-list')

    def form_valid(self, form):
        messages.success(self.request, 'Event updated successfully.')
        return super().form_valid(form)


class EventDeleteView(LoginRequiredMixin, ContentWriteMixin, DeleteView):
    model = Event
    template_name = 'events/event_confirm_delete.html'
    context_object_name = 'event'
    success_url = reverse_lazy('events:event-list')

    def post(self, request, *args, **kwargs):
        messages.success(request, 'Event deleted successfully.')
        return super().post(request, *args, **kwargs)


class EventRegisterView(LoginRequiredMixin, View):
    def post(self, request, pk):
        event = get_object_or_404(Event, pk=pk)

        if event.is_full:
            messages.error(request, 'This event is already at full capacity.')
            return redirect('events:event-detail', pk=event.pk)

        member_id = request.POST.get('member_id')

        if member_id:
            if not (request.user.is_authenticated and request.user.can_manage_content):
                messages.error(request, 'Only an admin or leader can register another member.')
                return redirect('events:event-detail', pk=event.pk)
            member = get_object_or_404(Member, pk=member_id)
        else:
            membership = getattr(request.user, 'member_profile', None)
            if membership is None:
                messages.error(
                    request,
                    'No member profile is linked to your account, so you cannot register yourself. '
                    'Ask an admin to register you instead.',
                )
                return redirect('events:event-detail', pk=event.pk)
            member = membership

        registration, created = EventRegistration.objects.get_or_create(
            event=event,
            member=member,
        )

        if created:
            messages.success(request, f'{member} has been registered for this event.')
        else:
            messages.info(request, f'{member} is already registered for this event.')

        return redirect('events:event-detail', pk=event.pk)


class EventRegistrationListView(LoginRequiredMixin, View):
    template_name = 'events/event_registration_list.html'

    def get(self, request, pk):
        event = get_object_or_404(Event, pk=pk)
        registrations = event.registrations.select_related('member').all()
        context = {
            'event': event,
            'registrations': registrations,
        }
        return render(request, self.template_name, context)
