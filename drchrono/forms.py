from django import forms

class CheckInSearchForm(forms.Form):
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)