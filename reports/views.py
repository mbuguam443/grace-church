from datetime import datetime

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Sum
from django.views.generic import TemplateView

from members.models import Member
from attendance.models import Attendance
from giving.models import Giving
from finance.models import Transaction
from visitors.models import Visitor


class ReportsHomeView(LoginRequiredMixin, TemplateView):
    template_name = 'reports/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_members'] = Member.objects.filter(membership_status='active').count()
        context['total_visitors'] = Visitor.objects.count()
        context['total_giving'] = Giving.objects.aggregate(total=Sum('amount'))['total'] or 0
        context['total_transactions'] = Transaction.objects.count()
        return context


class MembershipReportView(LoginRequiredMixin, TemplateView):
    template_name = 'reports/membership_report.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        members = Member.objects.all()

        start_date = self.request.GET.get('start_date', '').strip()
        end_date = self.request.GET.get('end_date', '').strip()

        if start_date:
            members = members.filter(date_joined__gte=start_date)
        if end_date:
            members = members.filter(date_joined__lte=end_date)

        context['members'] = members
        context['total'] = members.count()
        context['by_status'] = members.values('membership_status').annotate(count=Count('id')).order_by('membership_status')
        context['by_gender'] = members.values('gender').annotate(count=Count('id')).order_by('gender')
        context['by_type'] = members.values('membership_type').annotate(count=Count('id')).order_by('membership_type')
        context['by_marital_status'] = members.values('marital_status').annotate(count=Count('id')).order_by('marital_status')
        context['start_date'] = start_date
        context['end_date'] = end_date
        return context


class AttendanceReportView(LoginRequiredMixin, TemplateView):
    template_name = 'reports/attendance_report.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        attendances = Attendance.objects.all()

        start_date = self.request.GET.get('start_date', '').strip()
        end_date = self.request.GET.get('end_date', '').strip()

        if start_date:
            attendances = attendances.filter(service__date__gte=start_date)
        if end_date:
            attendances = attendances.filter(service__date__lte=end_date)

        context['attendances'] = attendances
        context['total_records'] = attendances.count()
        context['by_type'] = attendances.values('attendance_type').annotate(count=Count('id')).order_by('attendance_type')
        context['by_service'] = attendances.values('service__name').annotate(count=Count('id')).order_by('-count')[:20]
        context['start_date'] = start_date
        context['end_date'] = end_date
        return context


class GivingReportView(LoginRequiredMixin, TemplateView):
    template_name = 'reports/giving_report.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        givings = Giving.objects.all()

        start_date = self.request.GET.get('start_date', '').strip()
        end_date = self.request.GET.get('end_date', '').strip()

        if start_date:
            givings = givings.filter(date__gte=start_date)
        if end_date:
            givings = givings.filter(date__lte=end_date)

        context['givings'] = givings
        context['total_amount'] = givings.aggregate(total=Sum('amount'))['total'] or 0
        context['total_records'] = givings.count()
        context['by_category'] = givings.values('giving_category').annotate(
            total=Sum('amount'), count=Count('id')
        ).order_by('-total')
        context['by_payment_method'] = givings.values('payment_method').annotate(
            total=Sum('amount'), count=Count('id')
        ).order_by('-total')
        context['start_date'] = start_date
        context['end_date'] = end_date
        return context


class FinanceReportView(LoginRequiredMixin, TemplateView):
    template_name = 'reports/finance_report.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        transactions = Transaction.objects.all()

        start_date = self.request.GET.get('start_date', '').strip()
        end_date = self.request.GET.get('end_date', '').strip()

        if start_date:
            transactions = transactions.filter(date__gte=start_date)
        if end_date:
            transactions = transactions.filter(date__lte=end_date)

        income = transactions.filter(transaction_type='income').aggregate(total=Sum('amount'))['total'] or 0
        expense = transactions.filter(transaction_type='expense').aggregate(total=Sum('amount'))['total'] or 0

        context['transactions'] = transactions
        context['total_income'] = income
        context['total_expense'] = expense
        context['net_balance'] = income - expense
        context['income_by_category'] = transactions.filter(transaction_type='income').values('category').annotate(
            total=Sum('amount'), count=Count('id')
        ).order_by('-total')
        context['expense_by_category'] = transactions.filter(transaction_type='expense').values('category').annotate(
            total=Sum('amount'), count=Count('id')
        ).order_by('-total')
        context['start_date'] = start_date
        context['end_date'] = end_date
        return context


class VisitorReportView(LoginRequiredMixin, TemplateView):
    template_name = 'reports/visitor_report.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        visitors = Visitor.objects.all()

        start_date = self.request.GET.get('start_date', '').strip()
        end_date = self.request.GET.get('end_date', '').strip()

        if start_date:
            visitors = visitors.filter(visit_date__gte=start_date)
        if end_date:
            visitors = visitors.filter(visit_date__lte=end_date)

        context['visitors'] = visitors
        context['total'] = visitors.count()
        context['by_status'] = visitors.values('follow_up_status').annotate(count=Count('id')).order_by('follow_up_status')
        context['by_how_they_heard'] = visitors.values('how_they_heard').annotate(count=Count('id')).order_by('-count')
        context['by_service'] = visitors.values('service_attended').annotate(count=Count('id')).order_by('-count')
        context['start_date'] = start_date
        context['end_date'] = end_date
        return context
