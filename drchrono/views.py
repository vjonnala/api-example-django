# Create your views here.

from django.shortcuts import render, render_to_response
from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail, BadHeaderError
from django.views.generic import TemplateView
from django.template import RequestContext
from datetime import datetime
import urllib2, HTMLParser
from smtplib import SMTPException
import requests


from django.contrib.auth import (
	authenticate,
	get_user_model,
	login,
	logout,
)

# Provides the user access token to provide the authentication to drchrono website
def get_user_access_token(user, provider='drchrono'):
    return user.social_auth.get(provider=provider).extra_data.get('access_token')

# Contains the process that is useful to display the list of patients whose birthday is on current date.
def dummy(request):
	access_token = get_user_access_token(request.user)
        headers = {'Authorization': 'Bearer %s' % access_token}
	# Get the list of all the patients using the drchrono API
        response = requests.get("https://drchrono.com/api/patients", headers=headers)
	data = response.json()
	# Holds the details of each user object
	uobj = []
	# Loop through all the results in the response to the /api/patients call. Extract all the list of user details and maintatin them in List<List<>>
	for i in range(0,len(data['results'])):
		lastname = data['results'][i]['last_name']
		firstname = data['results'][i]['first_name']
		bday = data['results'][i]['date_of_birth']
		email = data['results'][i]['email']
		id = data['results'][i]['id']
		temp_list = []
		# Check if birthday of the patient is given
		if bday is not None:
			# Get the patient's bithday -  date , time
			dt = datetime.strptime(bday, '%Y-%m-%d')
			# Get the current day's -  date , time
			cdt = datetime.strptime(str(datetime.today()), '%Y-%m-%d %H:%M:%S.%f')
			# Check of the current month and day matches the user's birthday!
			if cdt.year > dt.year and cdt.month == dt.month and cdt.day == dt.day:
				temp_list.append(lastname)
				temp_list.append(firstname)
				temp_list.append(bday)
				temp_list.append(email)
				temp_list.append(id)
				temp_list.append("false")
				uobj.append(temp_list)
	request.session['uobj'] = uobj # Since there is no access to database, store the user details in the session
	# Return the entire reponse to web page woth all the details
	return render_to_response('dummy.html',{"user":request.user,  "uobj":uobj}, context_instance=RequestContext(request))

# Extracts the selected users from the birthday page to send e-mail.
def send_view(request):
	access_token = get_user_access_token(request.user)
        headers = {'Authorization': 'Bearer %s' % access_token}
	# call the /api/users/current to get the email-id of current user
        response = requests.get("https://drchrono.com/api/users/current", headers=headers)
	data = response.json()
        response1 = requests.get("https://drchrono.com/api/doctors", headers=headers)
	data1 = response1.json()
	# get the email-id of current user
	my_email = data1['results'][0]['email']
	uobj = request.session.get('uobj');
	# Get the id's (which are the indices of the List<List<>>) based on the selected checkboxes of the patients
	some_ids = request.POST.getlist('checks')
	some_emails = []
	some_messages = []
	# Loop through the list indices and get his email, greeting message and call the send mail function to send the email
	for id in some_ids:
		s_email = uobj[int(id)][3]
		some_emails.append(s_email)
		s_message = request.POST.get('dumps+'+id)
		some_messages.append(s_message)
		status = send_email(request, my_email, s_email, s_message)
		uobj[int(id)][5] = status

	return render(request, 'dummy.html', {"user":request.user, "uobj":uobj}, context_instance=RequestContext(request)) 

#Handles the mail transger from current user to selected patients whiose birthday is on current date.
def send_email(request, sender_mail, receiver_mail, mail_text):
	print(sender_mail, receiver_mail, mail_text)
	subject = "Birthday Greetings"
	EMAIL_HOST_USER = 'saiavi.pandu@gmail.com'
	EMAIL_HOST_PASSWORD = '' # Password is made null.
	status = send_mail(subject, mail_text, "drchrono@drchrono.com", [receiver_mail], fail_silently=False, auth_user= EMAIL_HOST_USER, auth_password = EMAIL_HOST_PASSWORD)
	# Status is the number of mails send to the receiver. If it is not zero, then the delivery is failed. If not, it is success
	if status == 1:
		return "true"
	else:
		return "failed"

