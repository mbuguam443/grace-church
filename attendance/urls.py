from django.urls import path
from . import views

app_name = 'attendance'

urlpatterns = [
    path('', views.AttendanceListView.as_view(), name='attendance_list'),
    path('create/', views.AttendanceCreateView.as_view(), name='attendance_create'),
    path('service/<int:pk>/', views.AttendanceByServiceView.as_view(), name='by_service'),
    path('<int:pk>/delete/', views.AttendanceDeleteView.as_view(), name='attendance_delete'),
]
