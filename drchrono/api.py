import datetime as dt
import requests
import urllib


class ApiError(Exception):
    pass


class DrChrono(object):
    base_url = 'https://drchrono.com'
    ISO_8601_FORMAT = "%Y-%m-%dT%H:%M:%S"

    class Appointment(object):
        STATUS_ARRIVED = "Arrived"
        STATUS_IN_SESSION = "In Session"
        STATUS_COMPLETE = "Complete"
        STATUS_CONFIRMED = "Confirmed"
        STATUS_NOT_CONFIRMED = "Not Confirmed"
        STATUS_RESCHEDULED = "Rescheduled"
        STATUS_CANCELLED = "Cancelled"
        STATUS_NO_SHOW = "No Show"

    def __init__(self, access_token):
        self.access_token = access_token
        self.headers = {'Authorization': 'Bearer %s' % self.access_token}

    def annotate_appointment(self, a, fetch_patient=False):
        a['scheduled_time'] = dt.datetime.strptime(a['scheduled_time'], self.ISO_8601_FORMAT)
        a['end_time'] = a['scheduled_time'] + dt.timedelta(minutes=a['duration'])
        if fetch_patient:
            a['patient'] = self.get_patient(a['patient'])
        return a

    def retrieve_single(self, endpoint):
        response = requests.get(self.base_url + endpoint, headers=self.headers)
        if response.status_code != 200:
            raise ApiError(response.json())
        return response.json()

    def retreive_multi(self, endpoint, params):
        results = []
        url = self.base_url + endpoint + "?" + urllib.urlencode(params)

        while url:
            response = requests.get(url, headers=self.headers)
            data = response.json()
            if response.status_code != 200:
                raise ApiError(data)
            results.extend(data['results'])
            url = data['next']
        return results

    def update_single(self, endpoint, data):
        response = requests.put(self.base_url + endpoint, data=data, headers=self.headers)
        if response.status_code != 204:
            raise ApiError(response.json())
        return

    def get_appointments(self, **kwargs):
        """
        Retrieves a list of appointments.

        Filtering parameters:
            date : date : Only retrieve appointments that occur on the given date
            date_range : date range : Retrieve appointments in a time period (inclusive).
            doctor : integer : Only retrieve appointments for the doctor with the given ID
            office : integer : Only retrieve appointments for the office with the given ID
            patient : integer : Only retrieve appointments for the patient with the given ID
            since : timestamp : Only retrieve appointments that have been updated since a given date
        """
        if not kwargs.get('since') and not kwargs.get('date') and not kwargs.get('date_range'):
            raise ValueError('Must supply at least one of `since`, `date`, or `date_range`')

        fetch_patient = kwargs.pop('fetch_patient', False)
        appointments = self.retreive_multi('/api/appointments', kwargs)
        for a in appointments:
            a = self.annotate_appointment(a, fetch_patient)
        return appointments

    def get_appointment(self, id, fetch_patient=False):
        return self.annotate_appointment(self.retrieve_single('/api/appointments/%d' % id), fetch_patient)

    def put_appointment(self, id, data):
        """
        Updates an appointment record.

        Required parameters in data:
            doctor : integer : doctor id
            duration : integer : Length of the appointment in minutes. Optional if profile is provided.
            exam_room : integer : required : Index of the exam room that this appointment occurs in.
            office : integer : required : Office ID
            patient : integer or null : required : ID of this appointment's patient. Breaks have a null patient field.
            scheduled_time : timestamp : required : The starting time of the appointment
        """
        return self.update_single('/api/appointments/%d' % id, data)

    def get_patients_summary(self, **kwargs):
        """Retrives a list of patients

        Filtering parameters:
            date_of_birth : date : Limit to patients born on a given date
            doctor : integer : List patients for the doctor with the given ID
            email : string:
            first_name : string : Case-insensitive and includes partial matches
            since : timestamp : Only retrieve patients that have been updated since a given date

        """
        return self.retreive_multi('/api/patients', kwargs)

    def get_patient(self, id):
        return self.retrieve_single('/api/patients/%d' % id)

    def put_patient(self, id, data):
        """
        Updates a patient record.

        Required parameters in data:
            doctor : integer: ID of the patient's primary provider
            gender : string : One of "Male", "Female", or "Other"
        """
        return self.update_single('/api/patients/%d' % id, data)
