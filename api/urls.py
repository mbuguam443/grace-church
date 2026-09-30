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
    # Sunday School
    path('sunday-school/', views.sunday_school_list_view, name='sunday-school'),
    path('sunday-school/<int:course_id>/', views.sunday_school_detail_view, name='sunday-school-detail'),
    path('sunday-school/<int:course_id>/join/', views.sunday_school_join_view, name='sunday-school-join'),
    path('sunday-school/<int:course_id>/leave/', views.sunday_school_leave_view, name='sunday-school-leave'),
    path('sunday-school/<int:course_id>/comments/', views.sunday_school_comment_view, name='sunday-school-comments'),
    path('sunday-school/<int:course_id>/comments/<int:comment_id>/delete/',
         views.sunday_school_comment_delete_view, name='sunday-school-comment-delete'),
    # Bible study enrolment + discussion
    path('bible-study/<int:note_id>/join/', views.bible_study_join_view, name='bible-study-join'),
    path('bible-study/<int:note_id>/leave/', views.bible_study_leave_view, name='bible-study-leave'),
    path('bible-study/<int:note_id>/comments/', views.bible_study_comment_view, name='bible-study-comments'),
    # Children
    path('children/', views.children_view, name='children'),
    path('children/<int:child_id>/', views.child_detail_view, name='child-detail'),
    path('children/<int:child_id>/checkin/', views.child_checkin_view, name='child-checkin'),
    path('children/<int:child_id>/checkout/', views.child_checkout_view, name='child-checkout'),
    # Giving
    path('give/', views.give_view, name='give'),
    # Directory
    path('members/', views.member_directory_view, name='directory'),
    path('members/<int:member_id>/', views.member_directory_detail_view, name='directory-detail'),
    path('ministries/', views.ministries_view, name='ministries'),
    path('ministries/<int:ministry_id>/', views.ministry_detail_view, name='ministry-detail'),
    path('groups/browse/', views.groups_browse_view, name='groups-browse'),
    path('groups/<int:group_id>/', views.group_detail_view, name='group-detail'),
    # Facilities
    path('facilities/', views.facilities_view, name='facilities'),
    path('facilities/bookings/', views.my_bookings_view, name='my-bookings'),
    # Single object details
    path('events/<int:event_id>/', views.event_detail_view, name='event-detail'),
    path('services/<int:service_id>/', views.service_detail_view, name='service-detail'),
]