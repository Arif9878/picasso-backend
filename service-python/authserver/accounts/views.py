from rest_framework import status, viewsets, permissions
from django.db.models import Q
from django.db.models import Value as V
from django.db.models.functions import Concat
from rest_framework.decorators import (
    api_view, permission_classes, authentication_classes)
from rest_framework.authentication import BasicAuthentication
from .models import Account
from .serializers import AccountSerializer, AccountClientAppSerializer
from rest_framework.response import Response
from authServer.keycloak import get_keycloak_user_id, set_user_password
from authServer.paginations import CustomPagination
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
            (Q(divisi="ASN")))
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
            keycloak_user_id = get_keycloak_user_id(user.email)
            set_user_password(keycloak_user_id, password)
            user.set_password(password)
            user.save()
            resp = { 'message': 'Ganti password berhasil' }
            return Response(resp, status=status.HTTP_201_CREATED)
    except:
        resp = { 'message': 'Ganti password gagal' }
        return Response(resp, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@authentication_classes([BasicAuthentication])
@permission_classes([permissions.AllowAny])
def client_user_list(request):
    page_query_param = 'page'
    page_size = request.query_params.get('page_size', None)
    paginator = CustomPagination()
    if page_size is not None:
        paginator.page_size = page_size
    paginator.page_query_param = page_query_param
    queryset = Account.objects.all()
    paginate = paginator.paginate_queryset(queryset=queryset, request=request)
    serializer = AccountClientAppSerializer(paginate, many=True)
    return paginator.get_paginated_response(serializer.data)
