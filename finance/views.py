from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q, Sum
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView, DeleteView, ListView, UpdateView, TemplateView,
)

from .models import Transaction


class FinanceAccessMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_finance

    def handle_no_permission(self):
        messages.error(self.request, 'You do not have permission to access finance records.')
        return super().handle_no_permission()


class FinanceDashboardView(LoginRequiredMixin, FinanceAccessMixin, TemplateView):
    template_name = 'finance/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        transactions = Transaction.objects.all()
        income = transactions.filter(transaction_type='income').aggregate(total=Sum('amount'))['total'] or 0
        expense = transactions.filter(transaction_type='expense').aggregate(total=Sum('amount'))['total'] or 0
        context['total_income'] = income
        context['total_expense'] = expense
        context['net_balance'] = income - expense
        context['recent_transactions'] = transactions[:10]
        context['transaction_count'] = transactions.count()
        return context


class TransactionListView(LoginRequiredMixin, FinanceAccessMixin, ListView):
    model = Transaction
    template_name = 'finance/transaction_list.html'
    context_object_name = 'transactions'
    paginate_by = 25

    def get_queryset(self):
        queryset = super().get_queryset()
        transaction_type = self.request.GET.get('type', '').strip()
        category = self.request.GET.get('category', '').strip()
        date_from = self.request.GET.get('date_from', '').strip()
        date_to = self.request.GET.get('date_to', '').strip()
        search = self.request.GET.get('search', '').strip()

        if transaction_type:
            queryset = queryset.filter(transaction_type=transaction_type)
        if category:
            queryset = queryset.filter(category=category)
        if date_from:
            queryset = queryset.filter(date__gte=date_from)
        if date_to:
            queryset = queryset.filter(date__lte=date_to)
        if search:
            queryset = queryset.filter(
                Q(description__icontains=search)
                | Q(category__icontains=search)
                | Q(member__first_name__icontains=search)
                | Q(member__last_name__icontains=search)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['type_filter'] = self.request.GET.get('type', '')
        context['category_filter'] = self.request.GET.get('category', '')
        context['date_from'] = self.request.GET.get('date_from', '')
        context['date_to'] = self.request.GET.get('date_to', '')
        context['search'] = self.request.GET.get('search', '')
        context['type_choices'] = Transaction.TYPE_CHOICES
        context['income_categories'] = Transaction.INCOME_CATEGORIES
        context['expense_categories'] = Transaction.EXPENSE_CATEGORIES
        return context


class TransactionCreateView(LoginRequiredMixin, FinanceAccessMixin, CreateView):
    model = Transaction
    template_name = 'finance/transaction_form.html'
    fields = ['transaction_type', 'amount', 'category', 'description', 'date', 'member']
    success_url = reverse_lazy('finance:transaction-list')

    def form_valid(self, form):
        form.instance.recorded_by = self.request.user
        messages.success(self.request, 'Transaction recorded successfully.')
        return super().form_valid(form)


class TransactionUpdateView(LoginRequiredMixin, FinanceAccessMixin, UpdateView):
    model = Transaction
    template_name = 'finance/transaction_form.html'
    fields = ['transaction_type', 'amount', 'category', 'description', 'date', 'member']
    success_url = reverse_lazy('finance:transaction-list')

    def form_valid(self, form):
        messages.success(self.request, 'Transaction updated successfully.')
        return super().form_valid(form)


class TransactionDeleteView(LoginRequiredMixin, FinanceAccessMixin, DeleteView):
    model = Transaction
    template_name = 'finance/transaction_confirm_delete.html'
    context_object_name = 'transaction'
    success_url = reverse_lazy('finance:transaction-list')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Transaction deleted successfully.')
        return super().delete(request, *args, **kwargs)
