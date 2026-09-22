from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DetailView, DeleteView
from accounts.views import ContentWriteMixin
from .models import Service


class ServiceListView(LoginRequiredMixin, ListView):
    model = Service
    template_name = 'services/service_list.html'
    context_object_name = 'services'
    paginate_by = 20


class ServiceCreateView(LoginRequiredMixin, ContentWriteMixin, CreateView):
    model = Service
    template_name = 'services/service_form.html'
    fields = ['name', 'date', 'start_time', 'end_time', 'location', 'preacher', 'theme', 'bible_verse', 'notes']
    success_url = reverse_lazy('services:service_list')

    def form_valid(self, form):
        messages.success(self.request, 'Service created successfully.')
        return super().form_valid(form)


class ServiceUpdateView(LoginRequiredMixin, ContentWriteMixin, UpdateView):
    model = Service
    template_name = 'services/service_form.html'
    fields = ['name', 'date', 'start_time', 'end_time', 'location', 'preacher', 'theme', 'bible_verse', 'notes']
    success_url = reverse_lazy('services:service_list')

    def form_valid(self, form):
        messages.success(self.request, 'Service updated successfully.')
        return super().form_valid(form)


class ServiceDetailView(LoginRequiredMixin, DetailView):
    model = Service
    template_name = 'services/service_detail.html'
    context_object_name = 'service'


class ServiceDeleteView(LoginRequiredMixin, ContentWriteMixin, DeleteView):
    model = Service
    template_name = 'services/service_confirm_delete.html'
    success_url = reverse_lazy('services:service_list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Service deleted successfully.')
        return super().delete(request, *args, **kwargs)
