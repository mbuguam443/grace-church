from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('', views.ReportsHomeView.as_view(), name='reports-home'),
    path('membership/', views.MembershipReportView.as_view(), name='membership-report'),
    path('attendance/', views.AttendanceReportView.as_view(), name='attendance-report'),
    path('giving/', views.GivingReportView.as_view(), name='giving-report'),
    path('finance/', views.FinanceReportView.as_view(), name='finance-report'),
    path('visitors/', views.VisitorReportView.as_view(), name='visitor-report'),
]
