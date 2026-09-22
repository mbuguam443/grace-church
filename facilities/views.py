from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import (
    CreateView, DeleteView, ListView, UpdateView, View,
)

from accounts.views import ContentWriteMixin
from .models import Facility, FacilityBooking


class FacilityListView(LoginRequiredMixin, ListView):
    model = Facility
    template_name = 'facilities/facility_list.html'
    context_object_name = 'facilities'
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.GET.get('search', '').strip()
        availability = self.request.GET.get('availability', '').strip()

        if search:
            queryset = queryset.filter(
                Q(name__icontains=search)
                | Q(location__icontains=search)
                | Q(description__icontains=search)
            )
        if availability == 'available':
            queryset = queryset.filter(is_available=True)
        elif availability == 'unavailable':
            queryset = queryset.filter(is_available=False)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        context['availability_filter'] = self.request.GET.get('availability', '')
        return context


class FacilityCreateView(LoginRequiredMixin, ContentWriteMixin, CreateView):
    model = Facility
    template_name = 'facilities/facility_form.html'
    fields = ['name', 'description', 'capacity', 'location', 'is_available']
    success_url = reverse_lazy('facilities:facility-list')

    def form_valid(self, form):
        messages.success(self.request, 'Facility created successfully.')
        return super().form_valid(form)


class FacilityUpdateView(LoginRequiredMixin, ContentWriteMixin, UpdateView):
    model = Facility
    template_name = 'facilities/facility_form.html'
    fields = ['name', 'description', 'capacity', 'location', 'is_available']
    success_url = reverse_lazy('facilities:facility-list')

    def form_valid(self, form):
        messages.success(self.request, 'Facility updated successfully.')
        return super().form_valid(form)


class FacilityDeleteView(LoginRequiredMixin, ContentWriteMixin, DeleteView):
    model = Facility
    template_name = 'facilities/facility_confirm_delete.html'
    context_object_name = 'facility'
    success_url = reverse_lazy('facilities:facility-list')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Facility deleted successfully.')
        return super().delete(request, *args, **kwargs)


class BookingListView(LoginRequiredMixin, ListView):
    model = FacilityBooking
    template_name = 'facilities/booking_list.html'
    context_object_name = 'bookings'
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.GET.get('search', '').strip()
        status = self.request.GET.get('status', '').strip()
        facility = self.request.GET.get('facility', '').strip()

        if search:
            queryset = queryset.filter(
                Q(event_name__icontains=search)
                | Q(purpose__icontains=search)
                | Q(booked_by__first_name__icontains=search)
                | Q(booked_by__last_name__icontains=search)
            )
        if status:
            queryset = queryset.filter(status=status)
        if facility:
            queryset = queryset.filter(facility_id=facility)

        return queryset.select_related('facility', 'booked_by')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        context['status_filter'] = self.request.GET.get('status', '')
        context['facility_filter'] = self.request.GET.get('facility', '')
        context['status_choices'] = FacilityBooking.STATUS_CHOICES
        context['facilities'] = Facility.objects.all()
        return context


class BookingCreateView(LoginRequiredMixin, CreateView):
    model = FacilityBooking
    template_name = 'facilities/booking_form.html'
    fields = [
        'facility', 'booked_by', 'event_name', 'date',
        'start_time', 'end_time', 'purpose', 'notes',
    ]
    success_url = reverse_lazy('facilities:booking-list')

    def form_valid(self, form):
        messages.success(self.request, 'Booking created successfully.')
        return super().form_valid(form)


class BookingUpdateView(LoginRequiredMixin, ContentWriteMixin, UpdateView):
    model = FacilityBooking
    template_name = 'facilities/booking_form.html'
    fields = [
        'facility', 'booked_by', 'event_name', 'date',
        'start_time', 'end_time', 'purpose', 'status', 'notes',
    ]
    success_url = reverse_lazy('facilities:booking-list')

    def form_valid(self, form):
        messages.success(self.request, 'Booking updated successfully.')
        return super().form_valid(form)


class BookingApproveView(LoginRequiredMixin, ContentWriteMixin, View):
    def post(self, request, pk):
        booking = get_object_or_404(FacilityBooking, pk=pk)
        booking.status = 'approved'
        booking.save()
        messages.success(request, f'Booking for "{booking.event_name}" has been approved.')
        return redirect('facilities:booking-list')


class BookingRejectView(LoginRequiredMixin, ContentWriteMixin, View):
    def post(self, request, pk):
        booking = get_object_or_404(FacilityBooking, pk=pk)
        booking.status = 'rejected'
        booking.save()
        messages.success(request, f'Booking for "{booking.event_name}" has been rejected.')
        return redirect('facilities:booking-list')
