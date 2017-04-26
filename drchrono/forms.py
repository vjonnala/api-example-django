from django import forms

from .enums import *
from .utils import add_blank_to_choices, choices_with_title


class CheckInSearchForm(forms.Form):
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)


class DemographicForm(forms.Form):
    first_name = forms.CharField(required=False)
    middle_name = forms.CharField(required=False)
    last_name = forms.CharField(required=False)
    date_of_birth = forms.DateField(required=True)
    gender = forms.ChoiceField(required=True, choices=(
        (GENDER_FEMALE, GENDER_FEMALE),
        (GENDER_MALE, GENDER_MALE),
        (GENDER_OTHER, GENDER_OTHER),
    ))
    social_security_number = forms.CharField(required=False)
    home_phone = forms.CharField(required=False)
    cell_phone = forms.CharField(required=False)
    address = forms.CharField(required=False)
    city = forms.CharField(required=False)
    state = forms.ChoiceField(required=False, choices=add_blank_to_choices(US_STATES))
    zip_code = forms.CharField(required=False)
    email = forms.CharField(required=False)
    ethnicity = forms.ChoiceField(required=False, choices=add_blank_to_choices(choices_with_title([
        ETHNICITY_BLANK,
        ETHNICITY_HISPANIC,
        ETHNICITY_NOT_HISPANIC,
        ETHNICITY_DECLINED,
    ])))
    race = forms.ChoiceField(required=False, choices=add_blank_to_choices(choices_with_title([
        RACE_BLACK,
        RACE_INDIAN,
        RACE_ASIAN,
        RACE_HAWAIIAN,
        RACE_WHITE,
        RACE_DECLINED,
    ])))

    emergency_contact_name = forms.CharField(required=False)
    emergency_contact_phone = forms.CharField(required=False)
    emergency_contact_relation = forms.CharField(required=False)

    employer = forms.CharField(required=False)
    employer_address = forms.CharField(required=False)
    employer_city = forms.CharField(required=False)
    employer_state = forms.ChoiceField(required=False, choices=add_blank_to_choices(US_STATES))
    employer_zip_code = forms.CharField(required=False)

    responsible_party_name = forms.CharField(required=False)
    responsible_party_relation = forms.CharField(required=False)
    responsible_party_phone = forms.CharField(required=False)
    responsible_party_email = forms.CharField(required=False)
