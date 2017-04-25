import datetime as dt

from django.shortcuts import redirect
from django.views.generic import TemplateView

from social_auth_drchrono.mixins import LoginRequiredMixin

from .api import DrChrono
from .utils import get_user_access_token

class LandingPageView(TemplateView):
    template_name = 'landing_page.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            return redirect('dashboard_view')
        return super(LandingPageView, self).dispatch(request, args, kwargs)

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard.html'

    def get_appointments(self):
        api = DrChrono(get_user_access_token(self.request.user))
        appointments = api.get_appointments(date=dt.date.today().isoformat())
        for a in appointments:
            a['patient'] = api.get_patient(a['patient'])
        return appointments

    def get_context_data(self, **kwargs):
        context = super(DashboardView, self).get_context_data(**kwargs)
        context['access_token'] = get_user_access_token(self.request.user)
        context['appointments'] = self.get_appointments()
        return context