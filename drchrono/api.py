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

    def retrieve_single(self, endpoint):
        response = requests.get(self.base_url + endpoint, headers=self.headers)
        if response.status_code != 200:
            raise ApiError(response.json())
        return response.json()

    def retreive_multi(self, endpoint, params):
        print params
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

    def get_appointments(self, **kwargs):
        """
        Retrieves a list of appointments.

        Filtering parameters:
            date : date : Only retrieve appointments that occur on the given date
            date_range : date range :Retrieve appointments in a time period (inclusive). Cannot be longer than 190 days, unless it is in the past.
            doctor : integer : Only retrieve appointments for the doctor with the given ID
            office : integer : Only retrieve appointments for the office with the given ID
            patient : integer : Only retrieve appointments for the patient with the given ID
            since : timestamp : Only retrieve appointments that have been updated since a given date
        """
        if not kwargs.get('since') and not kwargs.get('date') and not kwargs.get('date_range'):
            raise ValueError('Must supply at least one of `since`, `date`, or `date_range`')

        appointments = self.retreive_multi('/api/appointments', kwargs)
        for a in appointments:
            a['scheduled_time'] = dt.datetime.strptime(a['scheduled_time'], self.ISO_8601_FORMAT)
            a['end_time'] =  a['scheduled_time'] + dt.timedelta(minutes=a['duration'])
        return appointments

    def get_appointment(self, id):
        return self.retrieve_single('/api/appointments/%d' % id)

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
