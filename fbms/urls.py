from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('accounts/', include('accounts.urls')),
    path('members/', include('members.urls')),
    path('families/', include('families.urls')),
    path('visitors/', include('visitors.urls')),
    path('services/', include('services.urls')),
    path('attendance/', include('attendance.urls')),
    path('ministries/', include('ministries.urls')),
    path('groups/', include('groups.urls')),
    path('events/', include('events.urls')),
    path('finance/', include('finance.urls')),
    path('giving/', include('giving.urls')),
    path('prayer/', include('prayer.urls')),
    path('sermons/', include('sermons.urls')),
    path('children/', include('children.urls')),
    path('communication/', include('communication.urls')),
    path('assets/', include('assets.urls')),
    path('facilities/', include('facilities.urls')),
    path('reports/', include('reports.urls')),
    path('core/', include('core.urls')),
    path('songs/', include('songs.urls')),
    path('bible-study/', include('bible_study.urls')),
    path('sunday-school/', include('sunday_school.urls')),
    path('', include('public.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.BASE_DIR / 'static')
