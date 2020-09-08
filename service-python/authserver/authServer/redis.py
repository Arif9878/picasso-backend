from django.dispatch import receiver
from django.core.cache import cache
from datetime import datetime, timedelta
from itsdangerous import JSONWebSignatureSerializer
from .settings import (
    SECRET_KEY,
    SESSION_PREFIX,
    LOGIN_SESSION,
    REDIS_HOST,
    REDIS_PORT,
    REDIS_DB
    )
import redis
import json

r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)

def get_client_ip(request):
    ip = None
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')

    if x_forwarded_for:
        #ip = x_forwarded_for.split(',')[0]
        ip = x_forwarded_for.split(',')[-1].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
        
    return ip

def generate_token(user):
    s = JSONWebSignatureSerializer(SECRET_KEY)
    _user = {
        "id": str(user.id),
        "email": str(user.email),
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    token = s.dumps(_user)

    return token.decode('ASCII')

def generate_session(user, user_group, token, key):
    durasi = LOGIN_SESSION
    _created = datetime.now()
    seconds = durasi*(60**2)
    _expired = _created + timedelta(seconds=seconds)

    # Generate session data with active user
    # information so frontend should not
    # request multiple times
    return {
        "auth_token": str(token),
        "key": str(key),
        "created": _created.strftime("%Y-%m-%d %H:%M:%S"),
        "expired": _expired.strftime("%Y-%m-%d %H:%M:%S"),
        "durasi": durasi,
        "user": {
            "id": str(user.id),
            "email": user.email,
            "nama": user.nama,
            "satuan kerja": user_group
        }
    }


def save_session(session):
    # Get session prefix from config
    session_prefix = SESSION_PREFIX
    durasi = LOGIN_SESSION
    seconds = durasi*(60**2)
    # Clear all previous session
    token = session["auth_token"]
    clear_session(token=token)

    # Save session information
    r.set(
        "{}:{}:{}".format(
            session_prefix,
            session["auth_token"],
            session["user"]["email"]
        ),
        json.dumps(session),
        ex=seconds
    )

def get_user_session(nama=None, email=None, token=None, ip=None):

    list_all = []

    if email is not None:
        pattern = "*{}".format(email)
        has_session = r.keys(pattern)
    elif nama is not None:
        pattern = "*{}*".format(nama)
        has_session = r.keys(pattern)
    elif token is not None:
        pattern = "*{}*".format(nama)
        has_session = r.keys(pattern)
    else:
        pattern = "{}*".format(SESSION_PREFIX)
        has_session = r.keys(pattern)

    if has_session is not None:
        for key in has_session:
            data = json.loads(r.get(key).decode('ASCII'))
            list_all.append({'key': key, 'nama': data['user']['nama'],
                'email': data['user']['email'],
                'satuan kerja': data['user']['satuan kerja'],
                'ip': ip}
                )
    return list_all

def get_session_list(email=None, token=None):
    if email is not None:
        pattern = "*{}".format(email)
    elif token is not None:
        pattern = "*{}*".format(token)
    else:   
        return []

    return r.keys(pattern)

def get_session(email=None, token=None):

    if token is not None:
        pattern = "*{}*".format(token)
    elif email is not None:
        pattern = "*{}".format(email)
    # elif token is not None:
    #     pattern = "*{}*".format(token)
    # else:
    #     return None

    keys = r.keys(pattern)

    if len(keys) != 0:
        key = keys[0].decode('ASCII')
        session = r.get(key).decode('ASCII')
        return json.loads(session)
    else:
        return None

def clear_session(email=None, token=None):
    if email is not None:
        prev_session = get_session_list(email=email)
    elif token is not None:
        prev_session = get_session_list(token=token)

    if len(prev_session) > 0:
        prev_session = list(key.decode('ASCII') for key in prev_session)
        r.delete(*prev_session)


# @receiver(user_logged_in)
# def logon_log(sender, user, request, **kwargs):
#     # Ambil ip address user
#     ip = get_client_ip(request)

#     # Masukan informasi login ke database
#     logon_log = LogonLog.objects.create(
#         user=user,
#         action='login',
#         ip_address=ip)


# @receiver(user_logged_out)
# def logout_log(sender, user, request, **kwargs):
#     # Clear Cache User Online
#     # cache.delete('seen_%s' % user.email)
#     # Ambil ip address user
#     ip = get_client_ip(request)

#     # Masukan informasi login ke database
#     logon_log = LogonLog.objects.create(
#         user=user,
#         action='logout',
#         ip_address=ip)

def count_page(count, limit):
        """
            Function to count the page
        """
        page = count / limit
        remain = count % limit

        if remain > 0:
            page = page + 1

        if page == 0:
            page = 1

        return page
