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


class CheckOutSurveyResponse(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    appointment = models.IntegerField()

    ANSWER_DEFINITELY = 'Yes, Definitely'
    ANSWER_SOMEWHAT = 'Yes, Somewhat'
    ANSWER_NO = 'No'
    answer_choices = [(a, a) for a in [ANSWER_DEFINITELY, ANSWER_SOMEWHAT, ANSWER_NO]]

    q_explain = models.CharField(
        verbose_name="Did the doctor explain things in a way that was easy to understand?",
        choices=answer_choices,
        max_length=20,
    )
    q_listening = models.CharField(
        verbose_name="Did the doctor listen carefully to you?",
        choices=answer_choices,
        max_length=20,
    )
    q_instructions = models.CharField(
        verbose_name="Did the doctor give you easy to understand instructions about taking care of your health problems or concerns?",
        choices=answer_choices,
        max_length=20,
    )
    q_history = models.CharField(
        verbose_name="Did the doctor seem to know the important information about your medical history?",
        choices=answer_choices,
        max_length=20,
    )
    q_respect = models.CharField(
        verbose_name="Did the doctor show respect for what you had to say?",
        choices=answer_choices,
        max_length=20,
    )