import datetime as dt

from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, JsonResponse, QueryDict
from django.shortcuts import redirect
from django.views.generic import FormView, TemplateView, View

from social_auth_drchrono.mixins import LoginRequiredMixin

from .api import ApiError, DrChrono
from .forms import CheckInSearchForm, DemographicForm
from .models import AppointmentStatusHistory
from .utils import get_user_access_token


class LandingPageView(TemplateView):
    template_name = 'landing_page.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            return redirect('checkin_view')
        return super(LandingPageView, self).dispatch(request, args, kwargs)


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard.html'


class CheckInView(LoginRequiredMixin, TemplateView):
    template_name = 'checkin.html'

    def get_context_data(self, **kwargs):
        context = super(CheckInView, self).get_context_data(**kwargs)
        if self.request.GET:
            search_query = CheckInSearchForm(self.request.GET)
            if search_query.is_valid():
                api = DrChrono(get_user_access_token(self.request.user))
                first_name = search_query.cleaned_data['first_name']
                last_name = search_query.cleaned_data['last_name']
                a = None
                for a in api.get_appointments(date=dt.date.today().isoformat()):
                    a['patient'] = api.get_patient(a['patient'])
                    if a['patient']['first_name'] == first_name and a['patient']['last_name'] == last_name:
                        context['appointment'] = a
                        break
                if context.get('appointment'):
                    if a['status'] == DrChrono.Appointment.STATUS_ARRIVED:
                        messages.info(self.request, 'Your appointment has already been checked-in.')
                    elif a['status'] != DrChrono.Appointment.STATUS_CONFIRMED:
                        messages.warning(self.request,
                                         'Your appointment is not eligible for check-in (current status: %s).' %
                                         a['status'])
                else:
                    messages.error(self.request, 'No appointment was found for %s %s.' % (first_name, last_name))
        else:
            search_query = CheckInSearchForm()

        context['search_form'] = search_query
        context['status_confirmed'] = DrChrono.Appointment.STATUS_CONFIRMED
        return context


class VerifyRecordView(LoginRequiredMixin, FormView):
    form_class = DemographicForm
    template_name = 'verify.html'

    def dispatch(self, request, *args, **kwargs):
        self.api = DrChrono(get_user_access_token(request.user))
        self.appointment = self.api.get_appointment(int(self.kwargs['appointment']))
        self.patient = self.api.get_patient(int(self.appointment['patient']))
        return super(VerifyRecordView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(VerifyRecordView, self).get_context_data(**kwargs)
        context['appointment'] = self.appointment
        context['patient'] = self.patient
        return context

    def get_initial(self):
        return self.patient

    def form_valid(self, form):
        data = form.cleaned_data
        data.update({'doctor': self.patient['doctor']})
        appointment_id = int(self.appointment['id'])
        try:
            self.api.put_patient(self.patient['id'], data)
        except ApiError as e:
            messages.error(self.request, "There was an error when updating your information: %s" % str(e))
            return HttpResponseRedirect(reverse('verifyrecord_view', args=[appointment_id]))
        else:
            try:
                self.appointment['status'] = DrChrono.Appointment.STATUS_ARRIVED
                self.api.put_appointment(appointment_id, self.appointment)
            except ApiError as e:
                messages.error(self.request, 'There was an error when checking in for your appointment: %s' % str(e))
                return HttpResponseRedirect(reverse('verifyrecord_view', args=[appointment_id]))
            else:
                messages.success(self.request, 'You have successfully checked in for appointment.')
                a = AppointmentStatusHistory(appointment=appointment_id, status=DrChrono.Appointment.STATUS_ARRIVED)
                try:
                    a.save()
                except Exception as e:
                    messages.error(self.request, 'The kiosk was unable to record the time at which you checked-in.')
        return HttpResponseRedirect(reverse('checkin_view'))


class AjaxUpdateAppointmentStatus(View):
    http_method_names = [u'put']

    def put(self, request, *args, **kwargs):
        request.PUT = QueryDict(request.body)
        if 'appointment' not in request.PUT:
            return JsonResponse({'error':'appointment is required'}, status=400)
        if 'status' not in request.PUT:
            return JsonResponse({'error': 'status is required'}, status=400)
        api = DrChrono(get_user_access_token(request.user))
        appointment = api.get_appointment(int(request.PUT['appointment']))
        appointment['status'] = request.PUT['status']
        try:
            api.put_appointment(int(appointment['id']), appointment)
        except ApiError as e:
            return JsonResponse(
                {'error': 'An error occurred updating appointment %s: %s' % (appointment['id'], str(e))},
                 status=500
            )
        appointment = api.get_appointment(int(appointment['id']), fetch_patient=True)
        AppointmentStatusHistory.annotate_appointments([appointment])
        try:
            a = AppointmentStatusHistory(appointment=appointment['id'], status=request.PUT['status'])
            a.save()
        except Exception as e:
            return JsonResponse(
                {'error': 'An error occurred recording AppointmentStatusHistory %s/%s: %s' %
                          (appointment['id'], request.PUT['status'], str(e))},
                 status=500
            )
        return JsonResponse(appointment, status=200)

class AjaxGetAppointments(View):
    http_method_names = [u'get']

    def get(self, request, *args, **kwargs):
        api = DrChrono(get_user_access_token(request.user))
        appointments = api.get_appointments(date=dt.date.today().isoformat(), fetch_patient=True)
        AppointmentStatusHistory.annotate_appointments(appointments)
        return JsonResponse({'results': appointments}, status=200)
