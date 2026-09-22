from django.urls import path
from . import views

app_name = 'prayer'

urlpatterns = [
    path('', views.PrayerRequestListView.as_view(), name='prayer-request-list'),
    path('create/', views.PrayerRequestCreateView.as_view(), name='prayer-request-create'),
    path('<int:pk>/', views.PrayerRequestDetailView.as_view(), name='prayer-request-detail'),
    path('<int:pk>/update/', views.PrayerRequestUpdateView.as_view(), name='prayer-request-update'),
    path('<int:pk>/delete/', views.PrayerRequestDeleteView.as_view(), name='prayer-request-delete'),
]
