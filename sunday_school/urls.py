from django.urls import path
from . import views

app_name = 'sunday_school'

urlpatterns = [
    path('', views.CourseListView.as_view(), name='course_list'),
    path('create/', views.CourseCreateView.as_view(), name='course_create'),
    path('<int:pk>/', views.CourseDetailView.as_view(), name='course_detail'),
    path('<int:pk>/comment/', views.add_comment, name='course_comment'),
    path('<int:pk>/comment/<int:comment_id>/delete/', views.delete_comment, name='course_comment_delete'),
    path('<int:pk>/attachment/<str:attachment>/delete/', views.delete_attachment, name='course_attachment_delete'),
    path('<int:pk>/join/', views.join_course, name='course_join'),
    path('<int:pk>/leave/', views.leave_course, name='course_leave'),
    path('<int:pk>/add-student/', views.add_student, name='course_add_student'),
    path('<int:pk>/add-students/', views.add_students, name='course_add_students'),
    path('<int:pk>/enrollment/<int:enrollment_id>/approve/', views.approve_enrollment, name='course_enroll_approve'),
    path('<int:pk>/enrollment/<int:enrollment_id>/reject/', views.reject_enrollment, name='course_enroll_reject'),
    path('<int:pk>/enrollment/<int:enrollment_id>/remove/', views.remove_enrollment, name='course_enroll_remove'),
    path('<int:pk>/edit/', views.CourseUpdateView.as_view(), name='course_edit'),
    path('<int:pk>/delete/', views.CourseDeleteView.as_view(), name='course_delete'),
]