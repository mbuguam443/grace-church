from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('settings/', views.SettingsView.as_view(), name='settings'),
    path('leaders/', views.LeaderListView.as_view(), name='leaders'),
    path('leaders/add/', views.LeaderCreateView.as_view(), name='leader-add'),
    path('leaders/<int:pk>/edit/', views.LeaderUpdateView.as_view(), name='leader-edit'),
    path('leaders/<int:pk>/delete/', views.LeaderDeleteView.as_view(), name='leader-delete'),
]
