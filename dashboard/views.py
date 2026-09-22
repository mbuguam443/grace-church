from datetime import date, timedelta
from decimal import Decimal

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum
from django.utils import timezone
from django.views.generic import TemplateView

from attendance.models import Attendance
from communication.models import Announcement
from events.models import Event
from finance.models import Transaction
from giving.models import Giving
from members.models import Member
from prayer.models import PrayerRequest
from visitors.models import Visitor


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        today = date.today()
        first_of_month = today.replace(day=1)

        upcoming_events = Event.objects.filter(
            date__gte=today,
            is_active=True
        ).order_by('date', 'time')[:5]

        recent_announcements = Announcement.objects.filter(
            is_active=True
        ).order_by('-created_at')[:5]

        context['upcoming_events'] = upcoming_events
        context['recent_announcements'] = recent_announcements

        if user.is_admin_user or user.is_leader:
            total_members = Member.objects.count()
            active_members = Member.objects.filter(membership_status='active').count()
            visitors_count = Visitor.objects.count()

            todays_attendance = Attendance.objects.filter(
                service__date=today
            ).count()

            monthly_giving = Giving.objects.filter(
                date__gte=first_of_month,
                date__lte=today
            ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

            monthly_expenses = Transaction.objects.filter(
                transaction_type='expense',
                date__gte=first_of_month,
                date__lte=today
            ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

            pending_prayers = PrayerRequest.objects.filter(
                status__in=['new', 'assigned', 'in_progress']
            ).order_by('-created_at')[:5]

            context.update({
                'total_members': total_members,
                'active_members': active_members,
                'visitors_count': visitors_count,
                'todays_attendance': todays_attendance,
                'monthly_giving': monthly_giving,
                'monthly_expenses': monthly_expenses,
                'pending_prayers': pending_prayers,
                'is_admin_view': True,
            })
        else:
            try:
                member = Member.objects.get(user=user)
                my_attendance = Attendance.objects.filter(
                    member=member
                ).order_by('-service__date')[:10]
                my_giving = Giving.objects.filter(
                    member=member
                ).order_by('-date')[:10]
                my_groups = member.groups.all()
                my_events = Event.objects.filter(
                    date__gte=today,
                    is_active=True
                ).order_by('date')[:5]
                my_prayers = PrayerRequest.objects.filter(
                    member=member
                ).order_by('-created_at')[:5]

                context.update({
                    'member': member,
                    'my_attendance': my_attendance,
                    'my_giving': my_giving,
                    'my_groups': my_groups,
                    'my_events': my_events,
                    'my_prayers': my_prayers,
                    'is_admin_view': False,
                })
            except Member.DoesNotExist:
                context.update({
                    'member': None,
                    'is_admin_view': False,
                })

        return context
