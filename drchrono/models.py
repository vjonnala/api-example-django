from collections import defaultdict

from django.db import models

from .api import DrChrono


class AppointmentStatusHistory(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    appointment = models.IntegerField()
    status = models.CharField(max_length=20)

    class Meta:
        unique_together = ('appointment', 'status')

    @staticmethod
    def annotate_appointments(appointments):
        ids = [a['id'] for a in appointments]
        history = AppointmentStatusHistory.objects.filter(appointment__in=ids)
        lookup_table = defaultdict(dict)
        for h in history:
            lookup_table[h.appointment][h.status] = h.timestamp
        for a in appointments:
            if DrChrono.Appointment.STATUS_ARRIVED in lookup_table[int(a['id'])]:
                a['arrived'] = lookup_table[int(a['id'])][DrChrono.Appointment.STATUS_ARRIVED]
            if DrChrono.Appointment.STATUS_IN_SESSION in lookup_table[int(a['id'])]:
                a['session_begin'] = lookup_table[int(a['id'])][DrChrono.Appointment.STATUS_IN_SESSION]
            if DrChrono.Appointment.STATUS_COMPLETE in lookup_table[int(a['id'])]:
                a['session_end'] = lookup_table[int(a['id'])][DrChrono.Appointment.STATUS_COMPLETE]
