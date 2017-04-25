from django.db.models.fields import BLANK_CHOICE_DASH

def get_user_access_token(user, provider='drchrono'):
    return user.social_auth.get(provider=provider).extra_data.get('access_token')

def add_blank_to_choices(choices):
    return BLANK_CHOICE_DASH + list(choices)