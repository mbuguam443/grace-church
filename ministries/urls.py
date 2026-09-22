from django.urls import path

from . import views

app_name = 'ministries'

urlpatterns = [
    path('', views.MinistryListView.as_view(), name='ministry-list'),
    path('create/', views.MinistryCreateView.as_view(), name='ministry-create'),
    path('<int:pk>/', views.MinistryDetailView.as_view(), name='ministry-detail'),
    path('<int:pk>/update/', views.MinistryUpdateView.as_view(), name='ministry-update'),
    path('<int:pk>/delete/', views.MinistryDeleteView.as_view(), name='ministry-delete'),
]
