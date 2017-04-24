def get_user_access_token(user, provider='drchrono'):
    return user.social_auth.get(provider=provider).extra_data.get('access_token')