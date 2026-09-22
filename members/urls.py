from django.urls import path
from . import views

app_name = 'members'

urlpatterns = [
    path('', views.MemberListView.as_view(), name='member-list'),
    path('create/', views.MemberCreateView.as_view(), name='member-create'),
    path('<int:pk>/', views.MemberDetailView.as_view(), name='member-detail'),
    path('<int:pk>/update/', views.MemberUpdateView.as_view(), name='member-update'),
    path('<int:pk>/delete/', views.MemberDeleteView.as_view(), name='member-delete'),

    path('families/', views.FamilyListView.as_view(), name='family-list'),
    path('families/create/', views.FamilyCreateView.as_view(), name='family-create'),
    path('families/<int:pk>/', views.FamilyDetailView.as_view(), name='family-detail'),
    path('families/<int:pk>/update/', views.FamilyUpdateView.as_view(), name='family-update'),
    path('families/<int:pk>/delete/', views.FamilyDeleteView.as_view(), name='family-delete'),
]
