from django.conf.urls import include, url
from django.views.generic import TemplateView
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

import views


urlpatterns = [
    url(r'^$', TemplateView.as_view(template_name='index.html'), name='home'),

    url(r'^accounts/profile/',views.dummy, name="login"),

    url(r'', include('social.apps.django_app.urls', namespace='social')),

    url(r'^send/',views.send_view, name="send"),

]

urlpatterns += staticfiles_urlpatterns()
