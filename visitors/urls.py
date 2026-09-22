from django.urls import path
from . import views

app_name = 'visitors'

urlpatterns = [
    path('', views.VisitorListView.as_view(), name='visitor_list'),
    path('create/', views.VisitorCreateView.as_view(), name='visitor_create'),
    path('<int:pk>/', views.VisitorDetailView.as_view(), name='visitor_detail'),
    path('<int:pk>/edit/', views.VisitorUpdateView.as_view(), name='visitor_edit'),
    path('<int:pk>/delete/', views.VisitorDeleteView.as_view(), name='visitor_delete'),
]
