from django.conf.urls import include, url
from django.views.generic import TemplateView

from .views import DashboardView, LandingPageView


urlpatterns = [
    url(r'^$', LandingPageView.as_view(), name='landingpage_view'),
    url(r'^dashboard$', DashboardView.as_view(), name='dashboard_view'),
    url(r'', include('social.apps.django_app.urls', namespace='social')),
]
