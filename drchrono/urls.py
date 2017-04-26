from django.conf.urls import include, url
from django.views.generic import TemplateView

from .views import AjaxGetAppointments, \
    AjaxUpdateAppointmentStatus, \
    CheckInView, \
    CheckOutSurveyResponseCreateView, \
    CheckOutSurveyResponseListView, \
    DashboardView, \
    LandingPageView, \
    MetricsView, \
    SignCreateView, \
    SignListView, \
    VerifyRecordView


urlpatterns = [
    url(r'^$', LandingPageView.as_view(), name='landingpage_view'),
    url(r'^dashboard$', DashboardView.as_view(), name='dashboard_view'),
    url(r'^metrics$', MetricsView.as_view(), name='metrics_view'),
    url(r'^checkins$', CheckInView.as_view(), name='checkin_view'),
    url(r'^verify/(?P<appointment>\d+)$', VerifyRecordView.as_view(), name='verifyrecord_view'),
    url(r'^ajax/update_appointment_status$',
        AjaxUpdateAppointmentStatus.as_view(), name='ajax_update_appointment_status'),
    url(r'^ajax/get_appointments$', AjaxGetAppointments.as_view(), name='ajax_get_appointments'),

    # CheckOut Survey
    url(r'^checkout/(?P<appointment>\d+)', CheckOutSurveyResponseCreateView.as_view(), name='checkoutsurveyresponse_create'),
    url(r'^checkout/list', CheckOutSurveyResponseListView.as_view(), name='checkoutsurveyresponse_list'),

    # Digital Signage
    url(r'^sign/create$', SignCreateView.as_view(), name='sign_create'),
    url(r'^sign/list$', SignListView.as_view(), name='sign_list'),

    url(r'', include('social.apps.django_app.urls', namespace='social')),
]

from django.conf import settings
if settings.DEBUG == True:
    urlpatterns += [
        url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': settings.MEDIA_ROOT,
        })]