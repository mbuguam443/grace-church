from django.urls import path
from . import views

app_name = 'children'

urlpatterns = [
    path('', views.ChildListView.as_view(), name='child_list'),
    path('create/', views.ChildCreateView.as_view(), name='child_create'),
    path('<int:pk>/', views.ChildDetailView.as_view(), name='child_detail'),
    path('<int:pk>/edit/', views.ChildUpdateView.as_view(), name='child_edit'),
    path('<int:pk>/delete/', views.ChildDeleteView.as_view(), name='child_delete'),
    path('<int:pk>/checkin/', views.ChildCheckinView.as_view(), name='child_checkin'),
    path('<int:pk>/checkout/', views.ChildCheckoutView.as_view(), name='child_checkout'),
]
