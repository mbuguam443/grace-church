from django.urls import path
from django.views.generic import TemplateView

from .views import (
    PublicAboutView,
    PublicContactView,
    PublicEventsView,
    PublicGiveView,
    PublicHomeView,
    PublicMinistriesView,
    PublicSermonsView,
    PublicServicesView,
)

app_name = 'public'

urlpatterns = [
    path('', PublicHomeView.as_view(), name='home'),
    path('about-us/', PublicAboutView.as_view(), name='about'),
    path('our-ministries/', PublicMinistriesView.as_view(), name='ministries'),
    path('service-times/', PublicServicesView.as_view(), name='services'),
    path('upcoming-events/', PublicEventsView.as_view(), name='events'),
    path('our-sermons/', PublicSermonsView.as_view(), name='sermons'),
    path('contact-us/', PublicContactView.as_view(), name='contact'),
    path('give-now/', PublicGiveView.as_view(), name='give'),
    path('image-test/', TemplateView.as_view(template_name='public/image_test.html'), name='image_test'),
]
