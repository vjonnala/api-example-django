from collections import defaultdict
import datetime as dt

from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, JsonResponse, QueryDict
from django.shortcuts import redirect
from django.utils.timezone import make_aware
from django.views.generic import CreateView, FormView, ListView, TemplateView, View

from social_auth_drchrono.mixins import LoginRequiredMixin

from .api import ApiError, DrChrono
from .forms import CheckInSearchForm, DemographicForm
from .models import AppointmentStatusHistory, CheckOutSurveyResponse, Sign
from .utils import format_timedelta, get_user_access_token


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
        context['status_complete'] = DrChrono.Appointment.STATUS_COMPLETE
        context['signs'] = Sign.objects.all()
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
                messages.success(self.request, 'You have successfully checked in for your appointment.')
                a = AppointmentStatusHistory(appointment=appointment_id, status=DrChrono.Appointment.STATUS_ARRIVED)
                try:
                    a.save()
                except Exception as e:
                    messages.error(self.request, 'The kiosk was unable to record the time at which you checked-in.')
        return HttpResponseRedirect(reverse('checkin_view'))


class MetricsView(TemplateView):
    template_name = 'metrics.html'

    def dispatch(self, request, *args, **kwargs):
        self.history = AppointmentStatusHistory.objects.all()
        self.api = DrChrono(get_user_access_token(self.request.user))
        self.appointments = {ash.appointment: self.api.get_appointment(ash.appointment) for ash in self.history}
        return super(MetricsView, self).dispatch(request, *args, **kwargs)

    def get_wait_time(self):
        appointment_events = defaultdict(dict)
        for ash in self.history:
            appointment_events[ash.appointment][ash.status] = ash.timestamp
        wait_times = []
        for appointment, events in appointment_events.iteritems():
            if 'Arrived' in events and 'In Session' in events:
                wait_times.append(events['In Session'] - events['Arrived'])
        return {'mean': sum(wait_times, dt.timedelta(0))/len(wait_times),
                'count': len(wait_times)
                }

    def get_patient_tardiness(self):
        appointment_events = defaultdict(dict)
        for ash in self.history:
            appointment_events[ash.appointment][ash.status] = ash.timestamp
        arrival_deltas = []
        for appointment, events in appointment_events.iteritems():
            if 'Arrived' in events:
                app_details = self.appointments[appointment]
                delta = (events['Arrived'] - make_aware(app_details['scheduled_time']))
                arrival_deltas.append(delta)

        return {'mean': format_timedelta(sum(arrival_deltas, dt.timedelta(0))/len(arrival_deltas)),
                'count': len(arrival_deltas)
                }

    def get_appointment_efficiency(self):
        appointment_events = defaultdict(dict)
        for ash in self.history:
            appointment_events[ash.appointment][ash.status] = ash.timestamp
        efficiencies = []
        for appointment, events in appointment_events.iteritems():
            if 'Complete' in events:
                app_details = self.appointments[appointment]
                num = (events['Complete'] - events['In Session']).total_seconds()
                denom = int(app_details['duration'])*60
                efficiencies.append(num / denom)
        return {'mean': sum(efficiencies)/len(efficiencies),
                'count': len(efficiencies)
                }

    def get_pace_integrity(self):
        appointment_events = defaultdict(dict)
        for ash in self.history:
            appointment_events[ash.appointment][ash.status] = ash.timestamp
        paces = []
        for appointment, events in appointment_events.iteritems():
            if 'In Session' in events:
                app_details = self.appointments[appointment]
                paces.append(events['In Session'] - make_aware(app_details['scheduled_time']))
        return {'mean': format_timedelta(sum(paces, dt.timedelta(0))/len(paces)),
                'count': len(paces)
                }

    def get_context_data(self, **kwargs):
        context = super(MetricsView, self).get_context_data(**kwargs)
        context['wait_time'] = self.get_wait_time()
        context['patient_tardiness'] = self.get_patient_tardiness()
        context['appointment_efficiency'] = self.get_appointment_efficiency()
        context['pace_integrity'] = self.get_pace_integrity()
        return context


class AjaxUpdateAppointmentStatus(View):
    http_method_names = [u'put']

    def put(self, request, *args, **kwargs):
        request.PUT = QueryDict(request.body)
        if 'appointment' not in request.PUT:
            return JsonResponse({'error': 'appointment is required'}, status=400)
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


class CheckOutSurveyResponseCreateView(CreateView):
    model = CheckOutSurveyResponse
    fields = ['q_explain', 'q_listening', 'q_instructions', 'q_history', 'q_respect']

    def dispatch(self, request, *args, **kwargs):
        print kwargs
        if CheckOutSurveyResponse.objects.filter(appointment=kwargs['appointment']).exists():
            messages.warning(request, "You have already provided a survey response for that appointment.")
            return HttpResponseRedirect(self.get_success_url())
        self.api = DrChrono(get_user_access_token(request.user))
        self.appointment = self.api.get_appointment(int(kwargs['appointment']))
        return super(CheckOutSurveyResponseCreateView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(CheckOutSurveyResponseCreateView, self).get_context_data(**kwargs)
        context['appointment'] = self.appointment
        return context

    def get_success_url(self):
        return reverse('checkin_view')

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.appointment = self.appointment['id']
        self.object.save()
        messages.success(self.request, "Thank you for providing your feedback")
        return HttpResponseRedirect(self.get_success_url())


class CheckOutSurveyResponseListView(ListView):
    model = CheckOutSurveyResponse


class SignCreateView(CreateView):
    model = Sign
    fields = ['image', 'ordering']

    def get_success_url(self):
        return reverse('sign_list')


class SignListView(ListView):
    model = Sign
