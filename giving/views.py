from datetime import date

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q, Sum
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView, DeleteView, ListView, UpdateView,
)

from .models import Giving, OnlineGiving


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
        member = self.request.GET.get('member', '').strip() or self.request.GET.get('search', '').strip()
        giving_category = self.request.GET.get('giving_category', '').strip() or self.request.GET.get('category', '').strip()
        date_from = self.request.GET.get('date_from', '').strip()
        date_to = self.request.GET.get('date_to', '').strip()
        payment_method = self.request.GET.get('payment_method', '').strip()

        if member:
            queryset = queryset.filter(
                Q(member__first_name__icontains=member)
                | Q(member__last_name__icontains=member)
                | Q(member__member_number__icontains=member)
                | Q(notes__icontains=member)
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
        queryset = self.get_queryset()
        context['member_filter'] = self.request.GET.get('member', '')
        context['search'] = self.request.GET.get('search', '')
        context['category_filter'] = self.request.GET.get('giving_category', '') or self.request.GET.get('category', '')
        context['date_from'] = self.request.GET.get('date_from', '')
        context['date_to'] = self.request.GET.get('date_to', '')
        context['payment_filter'] = self.request.GET.get('payment_method', '')
        context['category_choices'] = Giving.GIVING_CATEGORIES
        context['payment_choices'] = Giving.PAYMENT_METHODS
        context['total_amount'] = (queryset.aggregate(t=Sum('amount'))['t'] or 0)
        context['contributor_count'] = queryset.exclude(member=None).values('member').distinct().count()
        context['monthly_total'] = (queryset.filter(date__year=date.today().year, date__month=date.today().month).aggregate(t=Sum('amount'))['t'] or 0)
        context['average_amount'] = (context['total_amount'] / queryset.count()) if queryset.count() else 0
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


class OnlineGivingListView(LoginRequiredMixin, FinanceAccessMixin, ListView):
    model = OnlineGiving
    template_name = 'giving/online_giving_list.html'
    context_object_name = 'online_givings'
    paginate_by = 25

    def get_queryset(self):
        queryset = super().get_queryset()
        status = self.request.GET.get('status', '').strip()
        search = self.request.GET.get('search', '').strip()
        if status:
            queryset = queryset.filter(status=status)
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search)
                | Q(email__icontains=search)
                | Q(reference_number__icontains=search)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_filter'] = self.request.GET.get('status', '')
        context['search'] = self.request.GET.get('search', '')
        context['status_choices'] = OnlineGiving.STATUS_CHOICES
        qs = self.get_queryset()
        context['total_online'] = (qs.aggregate(t=Sum('amount'))['t'] or 0)
        context['grand_total'] = (OnlineGiving.objects.aggregate(t=Sum('amount'))['t'] or 0)
        return context


class OnlineGivingDeleteView(LoginRequiredMixin, FinanceAccessMixin, DeleteView):
    model = OnlineGiving
    template_name = 'giving/online_giving_confirm_delete.html'
    context_object_name = 'online_giving'
    success_url = reverse_lazy('giving:online-giving-list')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Online giving submission removed.')
        return super().delete(request, *args, **kwargs)
