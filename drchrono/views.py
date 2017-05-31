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


def get_user_access_token(user, provider='drchrono'):
    return user.social_auth.get(provider=provider).extra_data.get('access_token')


def dummy(request):
	access_token = get_user_access_token(request.user)
        headers = {'Authorization': 'Bearer %s' % access_token}
        response = requests.get("https://drchrono.com/api/patients", headers=headers)
	data = response.json()
	uobj = []
	for i in range(0,len(data['results'])):
		lastname = data['results'][i]['last_name']
		firstname = data['results'][i]['first_name']
		bday = data['results'][i]['date_of_birth']
		email = data['results'][i]['email']
		id = data['results'][i]['id']
		temp_list = []
		if bday is not None:
			dt = datetime.strptime(bday, '%Y-%m-%d')
			cdt = datetime.strptime(str(datetime.today()), '%Y-%m-%d %H:%M:%S.%f')
			if cdt.year > dt.year and cdt.month == dt.month and cdt.day == dt.day:
				temp_list.append(lastname)
				temp_list.append(firstname)
				temp_list.append(bday)
				temp_list.append(email)
				temp_list.append(id)
				temp_list.append("false")
				uobj.append(temp_list)
	request.session['uobj'] = uobj
	return render_to_response('dummy.html',{"user":request.user,  "uobj":uobj}, context_instance=RequestContext(request))


def send_view(request):
	access_token = get_user_access_token(request.user)
        headers = {'Authorization': 'Bearer %s' % access_token}
        response = requests.get("https://drchrono.com/api/users/current", headers=headers)
	data = response.json()
        response1 = requests.get("https://drchrono.com/api/doctors", headers=headers)
	data1 = response1.json()	
	my_email = data1['results'][0]['email']
	uobj = request.session.get('uobj');
	some_ids = request.POST.getlist('checks')
	some_emails = []
	some_messages = []
	for id in some_ids:
		s_email = uobj[int(id)][3]
		some_emails.append(s_email)
		s_message = request.POST.get('dumps+'+id)
		some_messages.append(s_message)
		status = send_email(request, my_email, s_email, s_message)
		uobj[int(id)][5] = status

	return render(request, 'dummy.html', {"user":request.user, "uobj":uobj}, context_instance=RequestContext(request)) 

def send_email(request, sender_mail, receiver_mail, mail_text):
	print(sender_mail, receiver_mail, mail_text)
	subject = "Birthday Greetings"
	EMAIL_HOST_USER = 'saiavi.pandu@gmail.com'
	EMAIL_HOST_PASSWORD = 'karuna&avinash'
	status = send_mail(subject, mail_text, "drchrono@drchrono.com", [receiver_mail], fail_silently=False, auth_user= EMAIL_HOST_USER, auth_password = EMAIL_HOST_PASSWORD)
	if status == 1:
		return "true"
	else:
		return "failed"

