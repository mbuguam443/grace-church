from django.urls import path
from . import views

app_name = 'songs'

urlpatterns = [
    path('', views.SongListView.as_view(), name='song_list'),
    path('create/', views.SongCreateView.as_view(), name='song_create'),
    path('<int:pk>/', views.SongDetailView.as_view(), name='song_detail'),
    path('<int:pk>/edit/', views.SongUpdateView.as_view(), name='song_edit'),
    path('<int:pk>/delete/', views.SongDeleteView.as_view(), name='song_delete'),
]
