from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, View

from accounts.views import ContentWriteMixin
from .models import Event, EventRegistration


class EventListView(LoginRequiredMixin, ListView):
    model = Event
    template_name = 'events/event_list.html'
    context_object_name = 'events'


class EventDetailView(LoginRequiredMixin, DetailView):
    model = Event
    template_name = 'events/event_detail.html'
    context_object_name = 'event'


class EventCreateView(LoginRequiredMixin, ContentWriteMixin, CreateView):
    model = Event
    template_name = 'events/event_form.html'
    fields = ['name', 'description', 'date', 'time', 'end_date', 'location', 'organizer', 'speaker', 'capacity', 'registration_required', 'is_active']
    success_url = reverse_lazy('events:event-list')

    def form_valid(self, form):
        messages.success(self.request, 'Event created successfully.')
        return super().form_valid(form)


class EventUpdateView(LoginRequiredMixin, ContentWriteMixin, UpdateView):
    model = Event
    template_name = 'events/event_form.html'
    fields = ['name', 'description', 'date', 'time', 'end_date', 'location', 'organizer', 'speaker', 'capacity', 'registration_required', 'is_active']
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

        registration, created = EventRegistration.objects.get_or_create(
            event=event,
            member=request.user.member_profile,
        )

        if created:
            messages.success(self.request, 'You have successfully registered for this event.')
        else:
            messages.info(self.request, 'You are already registered for this event.')

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
