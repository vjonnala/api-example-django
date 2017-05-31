# drchrono Hackathon

### Requirements
- [pip](https://pip.pypa.io/en/stable/)
- [python virtual env](https://packaging.python.org/installing/#creating-and-using-virtual-environments)

### Setup
``` bash
$ pip install -r requirements.txt
$ python manage.py runserver
```

`social_auth_drchrono/` contains a custom provider for [Python Social Auth](http://psa.matiasaguirre.net/) that handles OAUTH for drchrono. To configure it, set these fields in your `drchrono/settings.py` file:

### Design
1) The page loads with the default welcome page with a Sign-In button
2) After the doctor enters the site with his credentials, a web page is displayed which contatins the list of all patients whose birthday is the current day!
3) Each list contatins a default-generated birthday greeting message , which can be later customized by the doctor.
4) The page disables the row if the email for the patient is not found!
5) The page has an option to select multiple rows which contains the list of patients, they need to send!
6) After selecting the list of patients, email is send to their account, with their repective greeting and status of the is displayed back.

**Future extensions:**
 -  e-cards or images in greeting
 - Timezone support
 - National Holidays and Regional Festivals
