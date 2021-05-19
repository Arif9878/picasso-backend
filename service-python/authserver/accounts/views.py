from rest_framework import status, viewsets, permissions
from django.contrib.auth.hashers import check_password
from django.db.models import Q
from django.db.models import Value as V
from django.db.models.functions import Concat
from rest_framework.decorators import (
    api_view, permission_classes)
from .models import Account, AccountEducation, AccountEmergencyContact, AccountFiles
from accounts.serializers import (
        AccountSerializer,
        AccountEducationSerializer,
        AccountEmergencyContactSerializer,
        AccountFilesSerializer
    )
from rest_framework.response import Response
from authServer.keycloak import get_keycloak_user_id, set_user_password

class AccountViewSet(viewsets.ModelViewSet):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer
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

class AccountEducationViewSet(viewsets.ModelViewSet):
    queryset = AccountEducation.objects.all()
    serializer_class = AccountEducationSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', 'post', 'put', 'delete', 'head']
    query = AccountEducation.objects.prefetch_related('account', 'graduation_year')

    def get_queryset(self):
        return self.queryset

class AccountEmergencyContactViewSet(viewsets.ModelViewSet):
    queryset = AccountEmergencyContact.objects.all()
    serializer_class = AccountEmergencyContactSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', 'post', 'put', 'delete', 'head']
    query = AccountEmergencyContact.objects.prefetch_related('account', 'emergency_contact_name', 'emergency_contact_number')

    def get_queryset(self):
        return self.queryset

class AccountFilesViewSet(viewsets.ModelViewSet):
    queryset = AccountFiles.objects.all()
    serializer_class = AccountFilesSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', 'post', 'put', 'delete', 'head']
    query = AccountFiles.objects.prefetch_related('account')

    def get_queryset(self):
        return self.queryset

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def change_password_admin(request, user_id):
    if request.user.is_admin:
        try:
            user = Account.objects.get(id=user_id)
            password = request.data.get('password')
            if user_id and password:
                keycloak_user_id = get_keycloak_user_id(user.email)
                if keycloak_user_id:
                    set_user_password(keycloak_user_id, password)
                user.set_password(password)
                user.save()
                resp = { 'message': 'Ganti password berhasil' }
                return Response(resp, status=status.HTTP_201_CREATED)
        except:
            resp = { 'message': 'Ganti password gagal' }
            return Response(resp, status=status.HTTP_400_BAD_REQUEST)
    return Response(status=status.HTTP_401_UNAUTHORIZED)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def change_password(request):
    resp = { 'message': 'Ganti password gagal' }
    try:
        user = Account.objects.get(email=request.user)
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')
        if user and check_password(old_password, user.password):
            keycloak_user_id = get_keycloak_user_id(user.email)
            if keycloak_user_id:
                set_user_password(keycloak_user_id, new_password)
            user.set_password(new_password)
            user.save()
            resp = { 'message': 'Ganti password berhasil' }
            return Response(resp, status=status.HTTP_201_CREATED)
        return Response(resp, status=status.HTTP_400_BAD_REQUEST)
    except:
        resp = { 'message': 'Ganti password gagal' }
        return Response(resp, status=status.HTTP_400_BAD_REQUEST)