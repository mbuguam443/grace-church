from django.urls import path
from . import views

app_name = 'bible_study'

urlpatterns = [
    path('', views.BibleStudyListView.as_view(), name='study_list'),
    path('create/', views.BibleStudyCreateView.as_view(), name='study_create'),
    path('<int:pk>/', views.BibleStudyDetailView.as_view(), name='study_detail'),
    path('<int:pk>/edit/', views.BibleStudyUpdateView.as_view(), name='study_edit'),
    path('<int:pk>/delete/', views.BibleStudyDeleteView.as_view(), name='study_delete'),
]
