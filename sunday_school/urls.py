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
    path('<int:pk>/edit/', views.CourseUpdateView.as_view(), name='course_edit'),
    path('<int:pk>/delete/', views.CourseDeleteView.as_view(), name='course_delete'),
]