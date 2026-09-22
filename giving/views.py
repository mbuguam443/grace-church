from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView, DeleteView, ListView, UpdateView,
)

from .models import Giving


class FinanceAccessMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_finance

    def handle_no_permission(self):
        messages.error(self.request, 'You do not have permission to access giving records.')
        return super().handle_no_permission()


class GivingListView(LoginRequiredMixin, FinanceAccessMixin, ListView):
    model = Giving
    template_name = 'giving/giving_list.html'
    context_object_name = 'givings'
    paginate_by = 25

    def get_queryset(self):
        queryset = super().get_queryset()
        member = self.request.GET.get('member', '').strip()
        giving_category = self.request.GET.get('giving_category', '').strip()
        date_from = self.request.GET.get('date_from', '').strip()
        date_to = self.request.GET.get('date_to', '').strip()
        payment_method = self.request.GET.get('payment_method', '').strip()

        if member:
            queryset = queryset.filter(
                Q(member__first_name__icontains=member)
                | Q(member__last_name__icontains=member)
                | Q(member__member_number__icontains=member)
            )
        if giving_category:
            queryset = queryset.filter(giving_category=giving_category)
        if date_from:
            queryset = queryset.filter(date__gte=date_from)
        if date_to:
            queryset = queryset.filter(date__lte=date_to)
        if payment_method:
            queryset = queryset.filter(payment_method=payment_method)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['member_filter'] = self.request.GET.get('member', '')
        context['category_filter'] = self.request.GET.get('giving_category', '')
        context['date_from'] = self.request.GET.get('date_from', '')
        context['date_to'] = self.request.GET.get('date_to', '')
        context['payment_filter'] = self.request.GET.get('payment_method', '')
        context['category_choices'] = Giving.GIVING_CATEGORIES
        context['payment_choices'] = Giving.PAYMENT_METHODS
        return context


class GivingCreateView(LoginRequiredMixin, FinanceAccessMixin, CreateView):
    model = Giving
    template_name = 'giving/giving_form.html'
    fields = ['member', 'amount', 'giving_category', 'date', 'payment_method', 'reference_number', 'notes']
    success_url = reverse_lazy('giving:giving-list')

    def form_valid(self, form):
        messages.success(self.request, 'Giving record created successfully.')
        return super().form_valid(form)


class GivingUpdateView(LoginRequiredMixin, FinanceAccessMixin, UpdateView):
    model = Giving
    template_name = 'giving/giving_form.html'
    fields = ['member', 'amount', 'giving_category', 'date', 'payment_method', 'reference_number', 'notes']
    success_url = reverse_lazy('giving:giving-list')

    def form_valid(self, form):
        messages.success(self.request, 'Giving record updated successfully.')
        return super().form_valid(form)


class GivingDeleteView(LoginRequiredMixin, FinanceAccessMixin, DeleteView):
    model = Giving
    template_name = 'giving/giving_confirm_delete.html'
    context_object_name = 'giving'
    success_url = reverse_lazy('giving:giving-list')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Giving record deleted successfully.')
        return super().delete(request, *args, **kwargs)
