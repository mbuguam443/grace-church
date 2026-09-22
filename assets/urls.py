from django.urls import path
from . import views

app_name = 'assets'

urlpatterns = [
    path('', views.AssetListView.as_view(), name='asset-list'),
    path('create/', views.AssetCreateView.as_view(), name='asset-create'),
    path('<int:pk>/', views.AssetDetailView.as_view(), name='asset-detail'),
    path('<int:pk>/update/', views.AssetUpdateView.as_view(), name='asset-update'),
    path('<int:pk>/delete/', views.AssetDeleteView.as_view(), name='asset-delete'),
]
