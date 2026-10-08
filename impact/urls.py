from django.urls import path

from . import views

app_name = 'impact'

urlpatterns = [
    path('stats/', views.ImpactStatsView.as_view(), name='stats'),
    path('', views.FundedPersonListView.as_view(), name='funded-list'),
    path('funded/create/', views.FundedPersonCreateView.as_view(), name='funded-create'),
    path('funded/<int:pk>/update/', views.FundedPersonUpdateView.as_view(), name='funded-update'),
    path('funded/<int:pk>/toggle-public/', views.FundedPersonTogglePublicView.as_view(), name='funded-toggle-public'),
    path('funded/<int:pk>/delete/', views.FundedPersonDeleteView.as_view(), name='funded-delete'),

    path('churches/', views.ChurchPlantListView.as_view(), name='churchplant-list'),
    path('churches/create/', views.ChurchPlantCreateView.as_view(), name='churchplant-create'),
    path('churches/<int:pk>/update/', views.ChurchPlantUpdateView.as_view(), name='churchplant-update'),
    path('churches/<int:pk>/delete/', views.ChurchPlantDeleteView.as_view(), name='churchplant-delete'),
]
