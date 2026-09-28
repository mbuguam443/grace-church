from django.urls import path
from . import views

app_name = 'giving'

urlpatterns = [
    path('', views.GivingListView.as_view(), name='giving-list'),
    path('create/', views.GivingCreateView.as_view(), name='giving-create'),
    path('online/', views.OnlineGivingListView.as_view(), name='online-giving-list'),
    path('online/<int:pk>/delete/', views.OnlineGivingDeleteView.as_view(), name='online-giving-delete'),
    path('<int:pk>/update/', views.GivingUpdateView.as_view(), name='giving-update'),
    path('<int:pk>/delete/', views.GivingDeleteView.as_view(), name='giving-delete'),
]