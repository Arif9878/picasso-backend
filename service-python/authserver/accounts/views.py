from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework import status, viewsets, permissions
from rest_framework.decorators import action
from django.db.models import Q
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
        idDivisi = self.request.query_params.get('idDivisi', None)
        blank = ""
        if search is not None and search is not blank:
            self.queryset = self.queryset.filter(
                (Q(username=search))|
                (Q(email=search))|
                (Q(first_name__icontains=search))|
                (Q(last_name__icontains=search)))
        if idDivisi is not None and idDivisi is not blank:
            self.queryset = self.queryset.filter(
                (Q(id_divisi=idDivisi)))
        return self.queryset

    def post(self, request, format=None):
        serializer = AccountSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
