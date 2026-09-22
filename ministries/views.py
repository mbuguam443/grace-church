from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from accounts.views import ContentWriteMixin
from .models import Ministry


class MinistryListView(LoginRequiredMixin, ListView):
    model = Ministry
    template_name = 'ministries/ministry_list.html'
    context_object_name = 'ministries'


class MinistryDetailView(LoginRequiredMixin, DetailView):
    model = Ministry
    template_name = 'ministries/ministry_detail.html'
    context_object_name = 'ministry'


class MinistryCreateView(LoginRequiredMixin, ContentWriteMixin, CreateView):
    model = Ministry
    template_name = 'ministries/ministry_form.html'
    fields = ['name', 'description', 'leader', 'members', 'is_active']
    success_url = reverse_lazy('ministries:ministry-list')

    def form_valid(self, form):
        messages.success(self.request, 'Ministry created successfully.')
        return super().form_valid(form)


class MinistryUpdateView(LoginRequiredMixin, ContentWriteMixin, UpdateView):
    model = Ministry
    template_name = 'ministries/ministry_form.html'
    fields = ['name', 'description', 'leader', 'members', 'is_active']
    success_url = reverse_lazy('ministries:ministry-list')

    def form_valid(self, form):
        messages.success(self.request, 'Ministry updated successfully.')
        return super().form_valid(form)


class MinistryDeleteView(LoginRequiredMixin, ContentWriteMixin, DeleteView):
    model = Ministry
    template_name = 'ministries/ministry_confirm_delete.html'
    context_object_name = 'ministry'
    success_url = reverse_lazy('ministries:ministry-list')

    def form_valid(self, form):
        messages.success(self.request, 'Ministry deleted successfully.')
        return super().form_valid(form)

    def post(self, request, *args, **kwargs):
        messages.success(request, 'Ministry deleted successfully.')
        return super().post(request, *args, **kwargs)
