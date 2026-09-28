from django.urls import path
from . import views

app_name = 'bible_study'

urlpatterns = [
    path('', views.BibleStudyListView.as_view(), name='study_list'),
    path('create/', views.BibleStudyCreateView.as_view(), name='study_create'),
    path('<int:pk>/', views.BibleStudyDetailView.as_view(), name='study_detail'),
    path('<int:pk>/comment/', views.add_comment, name='study_comment'),
    path('<int:pk>/comment/<int:comment_id>/delete/', views.delete_comment, name='study_comment_delete'),
    path('<int:pk>/attachment/<str:attachment>/delete/', views.delete_attachment, name='study_attachment_delete'),
    path('<int:pk>/edit/', views.BibleStudyUpdateView.as_view(), name='study_edit'),
    path('<int:pk>/delete/', views.BibleStudyDeleteView.as_view(), name='study_delete'),
]
