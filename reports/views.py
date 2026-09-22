from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Sum
from django.http import HttpResponse
from django.views.generic import TemplateView

from attendance.models import Attendance
from core.models import ChurchSetting
from finance.models import Transaction
from giving.models import Giving
from members.models import Member
from reports.pdf_utils import build_report_pdf
from visitors.models import Visitor


def _d(value):
    if not value:
        return '—'
    if hasattr(value, 'strftime'):
        try:
            return value.strftime('%b %d, %Y')
        except Exception:
            pass
    return str(value)


def _full_name(obj, fallback=''):
    fn = getattr(obj, 'get_full_name', None)
    if callable(fn):
        try:
            name = fn()
            if name:
                return name
        except Exception:
            pass
    parts = [
        getattr(obj, 'first_name', ''),
        getattr(obj, 'middle_name', ''),
        getattr(obj, 'last_name', ''),
    ]
    joined = ' '.join(p for p in parts if p).strip()
    return joined or fallback


def _display(obj, field, dash='—'):
    getter = getattr(obj, 'get_%s_display' % field, None)
    value = getattr(obj, field, '')
    if callable(getter):
        try:
            shown = getter()
            if shown:
                return str(shown)
        except Exception:
            pass
    return str(value) if value else dash


def _money(amount, currency):
    if amount is None or amount == '':
        return currency + ' 0.00'
    try:
        return '%s %s' % (currency, '{:,.2f}'.format(amount))
    except Exception:
        return str(amount)


class PDFReportMixin:
    pdf_title = 'Report'
    pdf_filename = 'report.pdf'

    def get(self, request, *args, **kwargs):
        if request.GET.get('format') == 'pdf':
            return self.pdf_response(request)
        return super().get(request, *args, **kwargs)

    def get_report(self):
        raise NotImplementedError

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(self.get_report()['context'])
        return context

    def pdf_response(self, request):
        data = self.get_report()
        logo = ChurchSetting.get_settings()
        currency = logo.currency or 'KES'
        period = data.get('period', '')
        subtitle = period or ''
        if period:
            subtitle += '   |   '
        subtitle += 'Generated automatically'
        pdf_bytes = build_report_pdf(
            title=self.pdf_title,
            subtitle=subtitle,
            columns=data['columns'],
            rows=data['rows'],
            summary=data.get('summary', []),
            right_align=data.get('right_align', set()),
            footer_left='%s | %s' % (logo.church_name or 'Grace Church Munyaka', self.pdf_title),
            church_line=logo.church_name or 'Grace Church Munyaka',
        )
        resp = HttpResponse(pdf_bytes, content_type='application/pdf')
        resp['Content-Disposition'] = 'attachment; filename="%s"' % self.pdf_filename
        return resp


class ReportsHomeView(LoginRequiredMixin, TemplateView):
    template_name = 'reports/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_members'] = Member.objects.filter(membership_status='active').count()
        context['total_visitors'] = Visitor.objects.count()
        context['total_giving'] = Giving.objects.aggregate(total=Sum('amount'))['total'] or 0
        context['total_transactions'] = Transaction.objects.count()
        return context


class MembershipReportView(LoginRequiredMixin, PDFReportMixin, TemplateView):
    template_name = 'reports/membership_report.html'
    pdf_title = 'Membership Report'
    pdf_filename = 'membership-report.pdf'

    def get_report(self):
        request = self.request
        start = (request.GET.get('start_date') or request.GET.get('date_from') or '').strip()
        end = (request.GET.get('end_date') or request.GET.get('date_to') or '').strip()
        status = (request.GET.get('status') or '').strip()
        gender = (request.GET.get('gender') or '').strip()

        qs = Member.objects.all()
        if start:
            qs = qs.filter(date_joined__gte=start)
        if end:
            qs = qs.filter(date_joined__lte=end)
        if status:
            qs = qs.filter(membership_status=status)
        if gender:
            qs = qs.filter(gender=gender)

        members = list(qs.order_by('-date_joined', 'first_name'))
        total = len(members)
        active = sum(1 for m in members if m.membership_status == 'active')
        inactive = total - active

        period = 'All time'
        if start and end:
            period = '%s – %s' % (start, end)
        elif start:
            period = 'From %s' % start
        elif end:
            period = 'Up to %s' % end

        context = {
            'members': members,
            'total': total,
            'by_status': qs.values('membership_status').annotate(count=Count('id')).order_by('membership_status'),
            'by_gender': qs.values('gender').annotate(count=Count('id')).order_by('gender'),
            'by_type': qs.values('membership_type').annotate(count=Count('id')).order_by('membership_type'),
            'by_marital_status': qs.values('marital_status').annotate(count=Count('id')).order_by('marital_status'),
            'start_date': start,
            'end_date': end,
            'total_members': total,
            'active_members': active,
        }

        rows = []
        for m in members:
            rows.append([
                _full_name(m, '—'),
                _display(m, 'gender'),
                m.phone or '—',
                m.email or '—',
                _d(m.date_joined),
                _display(m, 'membership_status'),
            ])

        return {
            'context': context,
            'period': period,
            'columns': ['Name', 'Gender', 'Phone', 'Email', 'Date Joined', 'Status'],
            'rows': rows,
            'summary': [
                ('Total', str(total)),
                ('Active', str(active)),
                ('Inactive', str(inactive)),
            ],
        }


class AttendanceReportView(LoginRequiredMixin, PDFReportMixin, TemplateView):
    template_name = 'reports/attendance_report.html'
    pdf_title = 'Attendance Report'
    pdf_filename = 'attendance-report.pdf'

    def get_report(self):
        request = self.request
        start = (request.GET.get('start_date') or request.GET.get('date_from') or '').strip()
        end = (request.GET.get('end_date') or request.GET.get('date_to') or '').strip()

        qs = Attendance.objects.select_related('service', 'member').all()
        if start:
            qs = qs.filter(service__date__gte=start)
        if end:
            qs = qs.filter(service__date__lte=end)

        attendances = list(qs.order_by('-service__date', '-created_at'))
        records = len(attendances)

        period = 'All time'
        if start and end:
            period = '%s – %s' % (start, end)
        elif start:
            period = 'From %s' % start
        elif end:
            period = 'Up to %s' % end

        by_type = qs.values('attendance_type').annotate(count=Count('id')).order_by('attendance_type')

        context = {
            'attendances': attendances,
            'total_records': records,
            'by_type': by_type,
            'by_service': qs.values('service__name').annotate(count=Count('id')).order_by('-count')[:20],
            'start_date': start,
            'end_date': end,
        }

        rows = []
        for a in attendances:
            service = a.service
            service_name = getattr(service, 'name', '') or '—'
            attendee = _full_name(a.member, a.visitor_name or '—')
            rows.append([
                _d(getattr(service, 'date', None)),
                service_name,
                attendee,
                _display(a, 'attendance_type'),
            ])

        type_labels = {code: label for code, label in Attendance.ATTENDANCE_TYPE_CHOICES}

        return {
            'context': context,
            'period': period,
            'columns': ['Date', 'Service', 'Attendee', 'Type'],
            'rows': rows,
            'summary': [('Total records', str(records))] + [
                (type_labels.get(k.get('attendance_type'), str(k.get('attendance_type') or '—')),
                 str(k['count']))
                for k in by_type
            ],
        }


class GivingReportView(LoginRequiredMixin, PDFReportMixin, TemplateView):
    template_name = 'reports/giving_report.html'
    pdf_title = 'Giving Report'
    pdf_filename = 'giving-report.pdf'

    def get_report(self):
        request = self.request
        start = (request.GET.get('start_date') or request.GET.get('date_from') or '').strip()
        end = (request.GET.get('end_date') or request.GET.get('date_to') or '').strip()
        currency = ChurchSetting.get_settings().currency or 'KES'

        qs = Giving.objects.select_related('member').all()
        if start:
            qs = qs.filter(date__gte=start)
        if end:
            qs = qs.filter(date__lte=end)

        givings = list(qs.order_by('-date'))
        total_amount = sum((g.amount or 0) for g in givings)
        records = len(givings)

        period = 'All time'
        if start and end:
            period = '%s – %s' % (start, end)
        elif start:
            period = 'From %s' % start
        elif end:
            period = 'Up to %s' % end

        context = {
            'givings': givings,
            'total_amount': total_amount,
            'total_records': records,
            'by_category': qs.values('giving_category').annotate(total=Sum('amount'), count=Count('id')).order_by('-total'),
            'by_payment_method': qs.values('payment_method').annotate(total=Sum('amount'), count=Count('id')).order_by('-total'),
            'start_date': start,
            'end_date': end,
        }

        rows = []
        for g in givings:
            rows.append([
                _d(g.date),
                _full_name(g.member, '—'),
                _display(g, 'giving_category'),
                _money(g.amount, currency),
                _display(g, 'payment_method'),
                g.reference_number or '—',
            ])

        return {
            'context': context,
            'period': period,
            'columns': ['Date', 'Contributor', 'Type', 'Amount', 'Payment Method', 'Reference'],
            'rows': rows,
            'right_align': {3},
            'summary': [
                ('Total given', _money(total_amount, currency)),
                ('Records', str(records)),
            ],
        }


class FinanceReportView(LoginRequiredMixin, PDFReportMixin, TemplateView):
    template_name = 'reports/finance_report.html'
    pdf_title = 'Finance Report'
    pdf_filename = 'finance-report.pdf'

    def get_report(self):
        request = self.request
        start = (request.GET.get('start_date') or request.GET.get('date_from') or '').strip()
        end = (request.GET.get('end_date') or request.GET.get('date_to') or '').strip()
        currency = ChurchSetting.get_settings().currency or 'KES'

        qs = Transaction.objects.all()
        if start:
            qs = qs.filter(date__gte=start)
        if end:
            qs = qs.filter(date__lte=end)

        transactions = list(qs.order_by('-date'))
        income = sum((t.amount or 0) for t in transactions if t.transaction_type == 'income')
        expense = sum((t.amount or 0) for t in transactions if t.transaction_type == 'expense')
        net = income - expense

        period = 'All time'
        if start and end:
            period = '%s – %s' % (start, end)
        elif start:
            period = 'From %s' % start
        elif end:
            period = 'Up to %s' % end

        context = {
            'transactions': transactions,
            'total_income': income,
            'total_expense': expense,
            'net_balance': net,
            'income_by_category': qs.filter(transaction_type='income').values('category').annotate(total=Sum('amount'), count=Count('id')).order_by('-total'),
            'expense_by_category': qs.filter(transaction_type='expense').values('category').annotate(total=Sum('amount'), count=Count('id')).order_by('-total'),
            'start_date': start,
            'end_date': end,
        }

        rows = []
        for t in transactions:
            amount_str = _money(t.amount, currency)
            if t.transaction_type == 'expense':
                amount_str = '- ' + amount_str
            rows.append([
                _d(t.date),
                t.description or '—',
                t.category or '—',
                'Income' if t.transaction_type == 'income' else 'Expense',
                amount_str,
            ])

        return {
            'context': context,
            'period': period,
            'columns': ['Date', 'Description', 'Category', 'Type', 'Amount'],
            'rows': rows,
            'right_align': {4},
            'summary': [
                ('Total income', _money(income, currency)),
                ('Total expense', _money(expense, currency)),
                ('Net balance', _money(net, currency)),
            ],
        }


class VisitorReportView(LoginRequiredMixin, PDFReportMixin, TemplateView):
    template_name = 'reports/visitor_report.html'
    pdf_title = 'Visitor Report'
    pdf_filename = 'visitor-report.pdf'

    def get_report(self):
        request = self.request
        start = (request.GET.get('start_date') or request.GET.get('date_from') or '').strip()
        end = (request.GET.get('end_date') or request.GET.get('date_to') or '').strip()

        qs = Visitor.objects.all()
        if start:
            qs = qs.filter(visit_date__gte=start)
        if end:
            qs = qs.filter(visit_date__lte=end)

        visitors = list(qs.order_by('-visit_date'))
        total = len(visitors)

        period = 'All time'
        if start and end:
            period = '%s – %s' % (start, end)
        elif start:
            period = 'From %s' % start
        elif end:
            period = 'Up to %s' % end

        by_status = qs.values('follow_up_status').annotate(count=Count('id')).order_by('follow_up_status')

        context = {
            'visitors': visitors,
            'total': total,
            'by_status': by_status,
            'by_how_they_heard': qs.values('how_they_heard').annotate(count=Count('id')).order_by('-count'),
            'by_service': qs.values('service_attended').annotate(count=Count('id')).order_by('-count'),
            'start_date': start,
            'end_date': end,
        }

        rows = []
        for v in visitors:
            rows.append([
                _d(v.visit_date),
                '%s %s' % (v.first_name, v.last_name),
                v.phone or '—',
                v.email or '—',
                v.service_attended or '—',
                _display(v, 'follow_up_status'),
                v.how_they_heard or '—',
            ])

        return {
            'context': context,
            'period': period,
            'columns': ['Date', 'Name', 'Phone', 'Email', 'Service', 'Follow-up', 'How Heard'],
            'rows': rows,
            'summary': [('Total visitors', str(total))] + [
                (str(k.get('follow_up_status') or '—'), str(k['count']))
                for k in by_status
            ],
        }