from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework import status, viewsets, permissions
from rest_framework.decorators import action
from django.db.models import Q
from django.db.models import Value as V
from django.db.models.functions import Concat
# pagination, generics
from rest_framework.decorators import (
    api_view, permission_classes)
from .models import Account
from .serializers import AccountSerializer, AccountLoginSerializer
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from rest_framework.response import Response
from authServer.settings import TOKEN_KEY
from .utils import get_client_ip
from datetime import datetime, timedelta
import time

class AccountViewSet(viewsets.ModelViewSet):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer
    # pagination_class = LargeResultsSetPagination
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', 'post', 'put', 'delete', 'head']
    query = Account.objects.prefetch_related('groups', 'user_permissions')

    def get_queryset(self):
        """
        This view should return a list of all the purchases for
        the user as determined by the username portion of the URL.
        """
        search = self.request.query_params.get('search', None)
        struktural = self.request.query_params.get('struktural', None)
        id_divisi = self.request.query_params.get('id_divisi', None)
        is_active = self.request.query_params.get('is_active', None)
        blank = ""
        if struktural is not None and struktural is not blank:
            self.queryset = self.queryset.filter(
            (Q(divisi="Struktural")))
        # else:
        #     self.queryset = self.queryset.filter(~Q(divisi="Struktural"))
        if search is not None and search is not blank:
            self.queryset = self.queryset.annotate(fullname=Concat('first_name', V(' '), 'last_name')).\
                filter((Q(fullname__icontains=search))|
                (Q(username=search))|
                (Q(email=search)))
        if id_divisi is not None and id_divisi is not blank:
            self.queryset = self.queryset.filter(
                (Q(id_divisi=id_divisi)))
        if is_active is not None and is_active is not blank:
            self.queryset = self.queryset.filter(
                (Q(is_active=is_active.title())))
        return self.queryset

    def post(self, request, format=None):
        serializer = AccountSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def change_password(request, user_id):
    try:
        user = Account.objects.get(id=user_id)
        password = request.data.get('password')
        if user_id and password:
            user.set_password(password)
            user.save()
            resp = { 'message': 'Ganti password berhasil' }
            return Response(resp, status=status.HTTP_201_CREATED)
    except:
        resp = { 'message': 'Ganti password gagal' }
        return Response(resp, status=status.HTTP_400_BAD_REQUEST)