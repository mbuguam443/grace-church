from django.urls import path
from . import views

app_name = 'sermons'

urlpatterns = [
    path('', views.SermonListView.as_view(), name='sermon_list'),
    path('create/', views.SermonCreateView.as_view(), name='sermon_create'),
    path('<int:pk>/', views.SermonDetailView.as_view(), name='sermon_detail'),
    path('<int:pk>/edit/', views.SermonUpdateView.as_view(), name='sermon_edit'),
    path('<int:pk>/delete/', views.SermonDeleteView.as_view(), name='sermon_delete'),
]
