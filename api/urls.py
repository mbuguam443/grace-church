from django.urls import path

from . import views

app_name = 'api'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('me/', views.me_view, name='me'),
    path('portal/', views.portal_view, name='portal'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/password/', views.change_password_view, name='change_password'),
    path('groups/', views.groups_view, name='groups'),
    path('givings/', views.givings_view, name='givings'),
    path('attendance/', views.attendance_view, name='attendance'),
    path('services/', views.services_view, name='services'),
    path('services/<int:service_id>/attend/', views.service_attend_view, name='service_attend'),
    path('events/', views.events_view, name='events'),
    path('events/<int:event_id>/register/', views.event_register_view, name='event_register'),
    path('announcements/', views.announcements_view, name='announcements'),
    path('sermons/', views.sermons_view, name='sermons'),
    path('sermons/<int:sermon_id>/', views.sermon_detail_view, name='sermon_detail'),
    path('devotions/', views.devotions_view, name='devotions'),
    path('bible-study/', views.bible_study_view, name='bible_study'),
    path('bible-study/<int:note_id>/', views.bible_study_detail_view, name='bible_study_detail'),
    path('songs/', views.songs_view, name='songs'),
    path('songs/<int:song_id>/', views.song_detail_view, name='song_detail'),
    path('prayers/', views.prayers_view, name='prayers'),
    path('notifications/', views.notifications_view, name='notifications'),
    path('devices/', views.device_token_view, name='devices'),
]