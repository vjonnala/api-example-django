import datetime as dt

from django.contrib import messages
from django.shortcuts import redirect
from django.views.generic import ListView, TemplateView

from social_auth_drchrono.mixins import LoginRequiredMixin

from .api import DrChrono
from .forms import CheckInSearchForm
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

class CheckInView(LoginRequiredMixin, TemplateView):
    template_name = 'checkin.html'

    def get_context_data(self, **kwargs):
        context = super(CheckInView, self).get_context_data()
        if self.request.GET:
            search_query = CheckInSearchForm(self.request.GET)
            if search_query.is_valid():
                api = DrChrono(get_user_access_token(self.request.user))
                first_name = search_query.cleaned_data['first_name']
                last_name = search_query.cleaned_data['last_name']
                for a in api.get_appointments(date=dt.date.today().isoformat()):
                    a['patient'] = api.get_patient(a['patient'])
                    if a['patient']['first_name'] == first_name and a['patient']['last_name'] == last_name:
                        context['appointment'] = a
                        break
                if context.get('appointment'):
                    if a['status'] == DrChrono.Appointment.STATUS_ARRIVED:
                        messages.info(self.request, 'Your appointment has already been checked-in.')
                    elif a['status'] != DrChrono.Appointment.STATUS_CONFIRMED:
                        messages.warning(self.request, 'Your appointment is not eligible for check-in (current status: %s).' % a['status'])
                else:
                    messages.error(self.request, 'No appointment was found for %s %s.' % (first_name, last_name))
        else:
            search_query = CheckInSearchForm()

        context['search_form'] = search_query
        context['status_confirmed'] = DrChrono.Appointment.STATUS_CONFIRMED
        return context