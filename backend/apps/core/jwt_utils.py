from datetime import datetime, timedelta, timezone as dt_timezone

import jwt
from django.conf import settings


def _secret():
    return getattr(settings, 'SECRET_KEY', 'secret')


def create_access_token(user):
    payload = {
        'user_id': user.id,
        'type': 'access',
        'exp': datetime.now(dt_timezone.utc) + timedelta(hours=24),
    }
    return jwt.encode(payload, _secret(), algorithm='HS256')


def create_refresh_token(user):
    payload = {
        'user_id': user.id,
        'type': 'refresh',
        'exp': datetime.now(dt_timezone.utc) + timedelta(days=7),
    }
    return jwt.encode(payload, _secret(), algorithm='HS256')


def decode_token(token):
    return jwt.decode(token, _secret(), algorithms=['HS256'])
