import jwt, datetime
from django.contrib.auth import get_user_model
from django.db.models import Q
from rest_framework.response import Response
from rest_framework import exceptions
from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view, permission_classes
from django.views.decorators.csrf import get_token, ensure_csrf_cookie, csrf_protect
from .serializers import AccountLoginSerializer
from .utils import get_client_ip, generate_access_token, generate_refresh_token
from django.contrib.sessions.models import Session
from django.conf import settings
    
@api_view(['POST'])
@permission_classes([AllowAny])
@ensure_csrf_cookie
def login_view(request):
    User = get_user_model()
    username = request.data.get('username')
    password = request.data.get('password')
    response = Response()
    if (username is None) or (password is None):
        raise exceptions.AuthenticationFailed(
            'username and password required')

    user = User.objects.filter(Q(username=username)|Q(email=username)).first()
    if(user is None):
        raise exceptions.AuthenticationFailed('user not found')
    if (not user.check_password(password)):
        raise exceptions.AuthenticationFailed('wrong password')

    serialized_user = AccountLoginSerializer(user).data

    access_token = generate_access_token(user)
    refresh_token = generate_refresh_token(user)
    ip = get_client_ip(request)
    dt = datetime.datetime.utcnow() + datetime.timedelta(seconds=14420)
    expTime = int(round(dt.timestamp() * 1000))
    # response.set_cookie(key='refreshtoken', value=refresh_token, httponly=True)
    response.data = {
        'auth_token': access_token,
        'refresh_token': refresh_token,
        'ip' : ip,
        'exp': expTime
    }

    return response

@api_view(['POST'])
@permission_classes([AllowAny])
@ensure_csrf_cookie
def login_admin_view(request):
    User = get_user_model()
    username = request.data.get('username')
    password = request.data.get('password')
    response = Response()
    if (username is None) or (password is None):
        raise exceptions.AuthenticationFailed(
            'username and password required')

    user = User.objects.filter(Q(username=username)|Q(email=username)).first()
    if(user is None):
        raise exceptions.AuthenticationFailed('user not found')
    if (not user.check_password(password)):
        raise exceptions.AuthenticationFailed('wrong password')
    if (not user.is_admin):
        raise exceptions.AuthenticationFailed('user does not have access rights')

    serialized_user = AccountLoginSerializer(user).data

    access_token = generate_access_token(user)
    refresh_token = generate_refresh_token(user)
    ip = get_client_ip(request)
    dt = datetime.datetime.utcnow() + datetime.timedelta(seconds=14420)
    expTime = int(round(dt.timestamp() * 1000))
    # response.set_cookie(key='refreshtoken', value=refresh_token, httponly=True)
    response.data = {
        'auth_token': access_token,
        'refresh_token': refresh_token,
        'ip' : ip,
        'exp': expTime
    }

    return response

@api_view(['POST'])
@permission_classes([AllowAny])
def refresh_token_view(request):
    User = get_user_model()
    request.session.clear()
    refresh_token = password = request.data.get('refreshtoken')
    try:
        refresh_token
    except NameError:
        refresh_token = None
    if refresh_token is None:
        raise exceptions.AuthenticationFailed(
            'Authentication credentials were not provided.')
    try:
        payload = jwt.decode(
            refresh_token, settings.REFRESH_TOKEN_SECRET, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        raise exceptions.AuthenticationFailed(
            'expired refresh token, please login again.')

    user = User.objects.filter(id=payload.get('user_id')).first()
    if user is None:
        raise exceptions.AuthenticationFailed('User not found')

    if not user.is_active:
        raise exceptions.AuthenticationFailed('user is inactive')


    access_token = generate_access_token(user)
    refresh_token = generate_refresh_token(user)
    return Response({
        'auth_token': access_token,
        'refresh_token': refresh_token
    })
