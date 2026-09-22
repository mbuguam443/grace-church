from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView, DeleteView, DetailView, ListView, UpdateView,
)

from .models import Asset
from accounts.views import ContentWriteMixin


class AssetListView(LoginRequiredMixin, ListView):
    model = Asset
    template_name = 'assets/asset_list.html'
    context_object_name = 'assets'
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.GET.get('search', '').strip()
        category = self.request.GET.get('category', '').strip()
        condition = self.request.GET.get('condition', '').strip()

        if search:
            queryset = queryset.filter(
                Q(name__icontains=search)
                | Q(serial_number__icontains=search)
                | Q(location__icontains=search)
                | Q(assigned_department__icontains=search)
            )
        if category:
            queryset = queryset.filter(category__iexact=category)
        if condition:
            queryset = queryset.filter(condition=condition)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        context['category_filter'] = self.request.GET.get('category', '')
        context['condition_filter'] = self.request.GET.get('condition', '')
        context['condition_choices'] = Asset.CONDITION_CHOICES
        context['categories'] = Asset.objects.values_list('category', flat=True).distinct().order_by('category')
        return context


class AssetDetailView(LoginRequiredMixin, DetailView):
    model = Asset
    template_name = 'assets/asset_detail.html'
    context_object_name = 'asset'


class AssetCreateView(LoginRequiredMixin, ContentWriteMixin, CreateView):
    model = Asset
    template_name = 'assets/asset_form.html'
    fields = [
        'name', 'category', 'serial_number', 'purchase_date', 'value',
        'condition', 'location', 'assigned_department', 'notes', 'is_active',
    ]
    success_url = reverse_lazy('assets:asset-list')

    def form_valid(self, form):
        messages.success(self.request, 'Asset created successfully.')
        return super().form_valid(form)


class AssetUpdateView(LoginRequiredMixin, ContentWriteMixin, UpdateView):
    model = Asset
    template_name = 'assets/asset_form.html'
    fields = [
        'name', 'category', 'serial_number', 'purchase_date', 'value',
        'condition', 'location', 'assigned_department', 'notes', 'is_active',
    ]
    success_url = reverse_lazy('assets:asset-list')

    def form_valid(self, form):
        messages.success(self.request, 'Asset updated successfully.')
        return super().form_valid(form)


class AssetDeleteView(LoginRequiredMixin, ContentWriteMixin, DeleteView):
    model = Asset
    template_name = 'assets/asset_confirm_delete.html'
    context_object_name = 'asset'
    success_url = reverse_lazy('assets:asset-list')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Asset deleted successfully.')
        return super().delete(request, *args, **kwargs)
