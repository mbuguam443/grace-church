from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from accounts.views import ContentWriteMixin
from .models import Announcement


class AnnouncementListView(LoginRequiredMixin, ListView):
    model = Announcement
    template_name = 'communication/announcement_list.html'
    context_object_name = 'announcements'
    paginate_by = 15

    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.GET.get('search', '')
        target = self.request.GET.get('target', '')
        if search:
            queryset = queryset.filter(title__icontains=search) | queryset.filter(message__icontains=search)
        if target:
            queryset = queryset.filter(target_audience__iexact=target)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        context['target'] = self.request.GET.get('target', '')
        context['target_choices'] = Announcement.TARGET_CHOICES
        return context


class AnnouncementCreateView(LoginRequiredMixin, ContentWriteMixin, CreateView):
    model = Announcement
    template_name = 'communication/announcement_form.html'
    fields = ['title', 'message', 'target_audience', 'expiry_date', 'is_active']
    success_url = reverse_lazy('communication:announcement_list')

    def form_valid(self, form):
        messages.success(self.request, 'Announcement created successfully.')
        return super().form_valid(form)


class AnnouncementUpdateView(LoginRequiredMixin, ContentWriteMixin, UpdateView):
    model = Announcement
    template_name = 'communication/announcement_form.html'
    fields = ['title', 'message', 'target_audience', 'expiry_date', 'is_active']
    success_url = reverse_lazy('communication:announcement_list')

    def form_valid(self, form):
        messages.success(self.request, 'Announcement updated successfully.')
        return super().form_valid(form)


class AnnouncementDeleteView(LoginRequiredMixin, ContentWriteMixin, DeleteView):
    model = Announcement
    template_name = 'communication/announcement_confirm_delete.html'
    success_url = reverse_lazy('communication:announcement_list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Announcement deleted successfully.')
        return super().delete(request, *args, **kwargs)
