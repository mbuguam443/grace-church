from django.urls import path

from . import views

app_name = 'groups'

urlpatterns = [
    path('', views.GroupListView.as_view(), name='group-list'),
    path('create/', views.GroupCreateView.as_view(), name='group-create'),
    path('<int:pk>/', views.GroupDetailView.as_view(), name='group-detail'),
    path('<int:pk>/update/', views.GroupUpdateView.as_view(), name='group-update'),
    path('<int:pk>/delete/', views.GroupDeleteView.as_view(), name='group-delete'),
    path('<int:pk>/attendance/', views.GroupAttendanceView.as_view(), name='group-attendance'),
]
