from django.urls import path
from . import views

app_name = 'facilities'

urlpatterns = [
    path('', views.FacilityListView.as_view(), name='facility-list'),
    path('create/', views.FacilityCreateView.as_view(), name='facility-create'),
    path('<int:pk>/update/', views.FacilityUpdateView.as_view(), name='facility-update'),
    path('<int:pk>/delete/', views.FacilityDeleteView.as_view(), name='facility-delete'),

    path('bookings/', views.BookingListView.as_view(), name='booking-list'),
    path('bookings/create/', views.BookingCreateView.as_view(), name='booking-create'),
    path('bookings/<int:pk>/update/', views.BookingUpdateView.as_view(), name='booking-update'),
    path('bookings/<int:pk>/approve/', views.BookingApproveView.as_view(), name='booking-approve'),
    path('bookings/<int:pk>/reject/', views.BookingRejectView.as_view(), name='booking-reject'),
]
