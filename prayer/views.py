from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView, DeleteView, DetailView, ListView, UpdateView,
)

from accounts.views import ContentWriteMixin
from .models import PrayerRequest


class PrayerRequestListView(LoginRequiredMixin, ListView):
    model = PrayerRequest
    template_name = 'prayer/prayer_list.html'
    context_object_name = 'prayer_requests'
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset()
        status = self.request.GET.get('status', '').strip()
        category = self.request.GET.get('category', '').strip()
        search = self.request.GET.get('search', '').strip()

        if status:
            queryset = queryset.filter(status=status)
        if category:
            queryset = queryset.filter(category=category)
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search)
                | Q(request__icontains=search)
                | Q(member__first_name__icontains=search)
                | Q(member__last_name__icontains=search)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_filter'] = self.request.GET.get('status', '')
        context['category_filter'] = self.request.GET.get('category', '')
        context['search'] = self.request.GET.get('search', '')
        context['status_choices'] = PrayerRequest.STATUS_CHOICES
        context['category_choices'] = PrayerRequest.CATEGORY_CHOICES
        return context


class PrayerRequestDetailView(LoginRequiredMixin, DetailView):
    model = PrayerRequest
    template_name = 'prayer/prayer_detail.html'
    context_object_name = 'prayer_request'


class PrayerRequestCreateView(LoginRequiredMixin, CreateView):
    model = PrayerRequest
    template_name = 'prayer/prayer_form.html'
    fields = ['member', 'title', 'request', 'category', 'is_confidential']
    success_url = reverse_lazy('prayer:prayer-request-list')

    def form_valid(self, form):
        messages.success(self.request, 'Prayer request submitted successfully.')
        return super().form_valid(form)


class PrayerRequestUpdateView(LoginRequiredMixin, ContentWriteMixin, UpdateView):
    model = PrayerRequest
    template_name = 'prayer/prayer_form.html'
    fields = ['member', 'title', 'request', 'category', 'status', 'assigned_to', 'notes', 'is_confidential']
    success_url = reverse_lazy('prayer:prayer-request-list')

    def form_valid(self, form):
        messages.success(self.request, 'Prayer request updated successfully.')
        return super().form_valid(form)


class PrayerRequestDeleteView(LoginRequiredMixin, ContentWriteMixin, DeleteView):
    model = PrayerRequest
    template_name = 'prayer/prayer_confirm_delete.html'
    context_object_name = 'prayer_request'
    success_url = reverse_lazy('prayer:prayer-request-list')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Prayer request deleted successfully.')
        return super().delete(request, *args, **kwargs)
