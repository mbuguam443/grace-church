from django.urls import path
from . import views

app_name = 'families'

urlpatterns = [
    path('<int:pk>/', views.FamilyDetailView.as_view(), name='family_detail'),
    path('<int:family_pk>/add-member/', views.AddMemberToFamilyView.as_view(), name='add_member'),
    path('relationship/<int:pk>/remove/', views.RemoveMemberFromFamilyView.as_view(), name='remove_member'),
]
