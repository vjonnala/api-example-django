from django.conf.urls import include, url
from django.views.generic import TemplateView

from .views import AjaxGetAppointments, \
    AjaxUpdateAppointmentStatus, \
    CheckInView, \
    DashboardView, \
    LandingPageView, \
    VerifyRecordView


urlpatterns = [
    url(r'^$', LandingPageView.as_view(), name='landingpage_view'),
    url(r'^dashboard$', DashboardView.as_view(), name='dashboard_view'),
    url(r'^checkins$', CheckInView.as_view(), name='checkin_view'),
    url(r'^verify/(?P<appointment>\d+)$', VerifyRecordView.as_view(), name='verifyrecord_view'),
    url(r'^ajax/update_appointment_status$', AjaxUpdateAppointmentStatus.as_view(), name='ajax_update_appointment_status'),
    url(r'^ajax/get_appointments$', AjaxGetAppointments.as_view(), name='ajax_get_appointments'),
    url(r'', include('social.apps.django_app.urls', namespace='social')),
]
