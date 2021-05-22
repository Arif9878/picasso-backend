import requests
from django.db.models import Q
from rest_framework import serializers, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from .models import Account
from accounts.serializers import AccountSerializer
from rest_framework.utils import json
from oauth2client.client import flow_from_clientsecrets, FlowExchangeError
from .utils import get_client_ip, generate_access_token, generate_refresh_token
from authServer.settings import CLIENT_SECRETS
from authServer.keycloak import userinfo_keycloak
from datetime import datetime, timedelta

class SocialSerializer(serializers.Serializer):
    """
    Serializer which accepts an OAuth2 access token.
    """
    access_token = serializers.CharField(
        allow_blank=False,
        trim_whitespace=True,
    )


@api_view(['POST'])
@permission_classes([AllowAny])
def oauth2_signin(request):
    serializer = SocialSerializer(data=request.data)

    if serializer.is_valid(raise_exception=True):
        code = serializer.data['access_token']
        try:
            # Upgrade the authorization code into a credentials object
            oauth_flow = flow_from_clientsecrets(CLIENT_SECRETS, scope='')
            oauth_flow.redirect_uri = 'postmessage'
            credentials = oauth_flow.step2_exchange(code)
            PARAMS = { 'access_token': credentials.access_token }
            r = requests.get("https://www.googleapis.com/oauth2/v2/userinfo", params=PARAMS)
            data = json.loads(r.text)
            try:
                user = Account.objects.filter(Q(email=data['email'])).distinct()
                if user.exists() and user.count() == 1:
                    user_obj = user.first()
                else:
                    return Response(
                        {'errors': {
                            'message': 'User belum terdaftar',
                        }},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                ip = get_client_ip(request)
                access_token = generate_access_token(user_obj)
                refresh_token = generate_refresh_token(user_obj)
                dt = datetime.utcnow() + timedelta(seconds=14420)
                expTime = int(round(dt.timestamp() * 1000))
                response = {
                    'auth_token': access_token,
                    'refresh_token': refresh_token,
                    'ip' : ip,
                    'exp': expTime
                }
                return Response(response, status=status.HTTP_200_OK)
            except:
                return Response(status=status.HTTP_400_BAD_REQUEST)
        except FlowExchangeError as e:
            return Response(
                {'errors': {
                    'token': 'Invalid token',
                    'detail': str(e),
                }},
                status=status.HTTP_400_BAD_REQUEST,
            )

@api_view(['POST'])
@permission_classes([AllowAny])
def oauth_keycloak_signin(request):
    serializer = SocialSerializer(data=request.data)

    if serializer.is_valid(raise_exception=True):
        access_token = serializer.data['access_token']
        try:
            userinfo = userinfo_keycloak(access_token)
            try:
                user = Account.objects.filter(Q(email=userinfo['email'])).distinct()
                if user.exists() and user.count() == 1:
                    user_obj = user.first()
                else:
                    return Response(
                        {'errors': {
                            'message': 'User belum terdaftar',
                        }},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                ip = get_client_ip(request)
                access_token = generate_access_token(user_obj)
                refresh_token = generate_refresh_token(user_obj)
                dt = datetime.utcnow() + timedelta(seconds=14420)
                expTime = int(round(dt.timestamp() * 1000))
                response = {
                    'auth_token': access_token,
                    'refresh_token': refresh_token,
                    'ip' : ip,
                    'exp': expTime
                }
                return Response(response, status=status.HTTP_200_OK)
            except:
                return Response(status=status.HTTP_400_BAD_REQUEST)
        except FlowExchangeError as e:
            return Response(
                {'errors': {
                    'token': 'Invalid token',
                    'detail': str(e),
                }},
                status=status.HTTP_400_BAD_REQUEST,
            )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def detail_user(request):
    try:
        account = Account.objects.get(email=request.user)
        serializer = AccountSerializer(account)
        responseData = {
            'data': serializer.data
        }
        return Response(responseData, status=status.HTTP_200_OK)
    except:
        return Response(status=status.HTTP_400_BAD_REQUEST)

 

