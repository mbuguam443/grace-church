from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import models
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DetailView, DeleteView
from accounts.views import ContentWriteMixin
from .models import Visitor


class VisitorListView(LoginRequiredMixin, ListView):
    model = Visitor
    template_name = 'visitors/visitor_list.html'
    context_object_name = 'visitors'
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.GET.get('search', '')
        status = self.request.GET.get('status', '')

        if search:
            queryset = queryset.filter(
                models.Q(first_name__icontains=search) |
                models.Q(last_name__icontains=search) |
                models.Q(phone__icontains=search) |
                models.Q(email__icontains=search)
            )
        if status:
            queryset = queryset.filter(follow_up_status=status)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        context['status'] = self.request.GET.get('status', '')
        context['status_choices'] = Visitor.STATUS_CHOICES
        return context


class VisitorCreateView(LoginRequiredMixin, ContentWriteMixin, CreateView):
    model = Visitor
    template_name = 'visitors/visitor_form.html'
    fields = ['first_name', 'last_name', 'phone', 'email', 'visit_date', 'service_attended', 'how_they_heard', 'follow_up_status', 'assigned_to', 'notes']
    success_url = reverse_lazy('visitors:visitor_list')

    def form_valid(self, form):
        messages.success(self.request, 'Visitor created successfully.')
        return super().form_valid(form)


class VisitorUpdateView(LoginRequiredMixin, ContentWriteMixin, UpdateView):
    model = Visitor
    template_name = 'visitors/visitor_form.html'
    fields = ['first_name', 'last_name', 'phone', 'email', 'visit_date', 'service_attended', 'how_they_heard', 'follow_up_status', 'assigned_to', 'notes']
    success_url = reverse_lazy('visitors:visitor_list')

    def form_valid(self, form):
        messages.success(self.request, 'Visitor updated successfully.')
        return super().form_valid(form)


class VisitorDetailView(LoginRequiredMixin, DetailView):
    model = Visitor
    template_name = 'visitors/visitor_detail.html'
    context_object_name = 'visitor'


class VisitorDeleteView(LoginRequiredMixin, ContentWriteMixin, DeleteView):
    model = Visitor
    template_name = 'visitors/visitor_confirm_delete.html'
    success_url = reverse_lazy('visitors:visitor_list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Visitor deleted successfully.')
        return super().delete(request, *args, **kwargs)
