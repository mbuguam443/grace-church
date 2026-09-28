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
    path('<int:pk>/join/', views.join_study, name='study_join'),
    path('<int:pk>/leave/', views.leave_study, name='study_leave'),
    path('<int:pk>/add-student/', views.add_student, name='study_add_student'),
    path('<int:pk>/add-students/', views.add_students, name='study_add_students'),
    path('<int:pk>/enrollment/<int:enrollment_id>/approve/', views.approve_enrollment, name='study_enroll_approve'),
    path('<int:pk>/enrollment/<int:enrollment_id>/reject/', views.reject_enrollment, name='study_enroll_reject'),
    path('<int:pk>/enrollment/<int:enrollment_id>/remove/', views.remove_enrollment, name='study_enroll_remove'),
    path('<int:pk>/edit/', views.BibleStudyUpdateView.as_view(), name='study_edit'),
    path('<int:pk>/delete/', views.BibleStudyDeleteView.as_view(), name='study_delete'),
]
