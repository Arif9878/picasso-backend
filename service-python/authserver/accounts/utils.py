from rest_framework_jwt.settings import api_settings
import datetime, jwt
from django.conf import settings

def create_token(user):
    jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
    jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
    payload = jwt_payload_handler(user)
    payload['divisi'] = user.divisi
    payload['jabatan'] = user.jabatan
    token = jwt_encode_handler(payload)

    return token

def get_client_ip(request):
    ip = None
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')

    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[-1].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')

    return ip

def get_status_color(obj):
	warna = ""
	if obj.status == 2:
		warna = 'warning'
	elif obj.status == 3:
		warna = 'info'
	return warna

STATUS = (
	(1, 'Active'),
	(2, 'Archive'),
	(3, 'Draft'),
)

JENIS_KELAMIN = (
	('Pria', 'Pria'),
	('Wanita', 'Wanita')
)


def generate_access_token(user):

    access_token_payload = {
        'user_id': str(user.id),
        'fullname': user.get_full_name(),
        'email': user.email,
        'username': user.username,
        'divisi': user.divisi,
        'jabatan': user.jabatan,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=0, minutes=0, seconds=14420),
        'iat': datetime.datetime.utcnow(),
    }
    access_token = jwt.encode(access_token_payload,
                              settings.SECRET_KEY, algorithm='HS256').decode('utf-8')
    return access_token


def generate_refresh_token(user):
    refresh_token_payload = {
        'user_id': str(user.id),
        'fullname': user.get_full_name(),
        'email': user.email,
        'username': user.username,
        'divisi': user.divisi,
        'jabatan': user.jabatan,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=3),
        'iat': datetime.datetime.utcnow()
    }
    refresh_token = jwt.encode(
        refresh_token_payload, settings.REFRESH_TOKEN_SECRET, algorithm='HS256').decode('utf-8')

    return refresh_token

