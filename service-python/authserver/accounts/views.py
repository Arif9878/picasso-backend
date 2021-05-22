from rest_framework import status, viewsets, permissions
from django.contrib.auth.hashers import check_password
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.db.models import Value as V
from django.db.models.functions import Concat
from rest_framework.decorators import action
from rest_framework.decorators import (
    api_view, permission_classes, authentication_classes)
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.views import APIView
from .models import Account, AccountOtherInformation, AccountEducation, AccountEmergencyContact, AccountFiles
from accounts.serializers import (
        AccountSerializer,
        AccountOtherInformationSerializer,
        AccountEducationSerializer,
        AccountEmergencyContactSerializer,
        AccountFilesSerializer,
        AccountProfileSerializer,
        AccountClientAppSerializer
    )
from rest_framework.authentication import BasicAuthentication
from rest_framework.response import Response
from authServer.keycloak import get_keycloak_user_id, set_user_password
from authServer.paginations import CustomPagination
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
class AccountOtherInformationViewSet(viewsets.ModelViewSet):
    queryset = AccountOtherInformation.objects.all()
    serializer_class = AccountOtherInformationSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', 'post', 'put', 'delete', 'head']
    query = AccountOtherInformation.objects.prefetch_related('account')

    def get_queryset(self):
        self.queryset = self.queryset.filter(account=self.request.user).order_by('-account')
        return self.queryset

    # details account information for admin
    @action(detail=True, methods=['get'], permission_classes=[permissions.IsAdminUser])
    def details(self, request,  pk=None):
        try:
            account_other_info = AccountOtherInformation.objects.get(pk=pk)
            serializer = self.get_serializer(account_other_info)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except:
            return Response(status=status.HTTP_200_OK)

    # update account information for admin
    @action(detail=True, methods=['put'], permission_classes=[permissions.IsAdminUser])
    def updates(self, request, pk=None):
        if request.user.is_admin:
            try:
                account_other_info = AccountOtherInformation.objects.get(account_id=pk)
                serializer = self.get_serializer(account_other_info, data=request.data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return Response(serializer.data, status=status.HTTP_200_OK)
            except:
                account = get_object_or_404(Account, pk=pk)
                request.data['account'] = account
                account_other_info = AccountOtherInformation.objects.create(**request.data)
                serializer = self.get_serializer(account_other_info)
                return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_401_UNAUTHORIZED)

class AccountEducationViewSet(viewsets.ModelViewSet):
    queryset = AccountEducation.objects.all()
    serializer_class = AccountEducationSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', 'post', 'put', 'delete', 'head']
    query = AccountEducation.objects.prefetch_related('account', 'graduation_year')

    def get_queryset(self):
        self.queryset = self.queryset.filter(account=self.request.user).order_by('-graduation_year')
        return self.queryset

    # list account education for admin
    @action(detail=True, methods=['get'], permission_classes=[permissions.IsAdminUser])
    def lists(self, request,  pk=None):
        account_education = AccountEducation.objects.filter(account_id=pk).order_by('-graduation_year')

        page = self.paginate_queryset(account_education)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(account_education, many=True)
        return Response(serializer.data)

class AccountEmergencyContactViewSet(viewsets.ModelViewSet):
    queryset = AccountEmergencyContact.objects.all()
    serializer_class = AccountEmergencyContactSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', 'post', 'put', 'delete', 'head']
    query = AccountEmergencyContact.objects.prefetch_related('account', 'emergency_contact_name', 'emergency_contact_number')

    def get_queryset(self):
        self.queryset = self.queryset.filter(account=self.request.user).order_by('-created_at')
        return self.queryset

    # list account emergency contact for admin
    @action(detail=True, methods=['get'], permission_classes=[permissions.IsAdminUser])
    def lists(self, request,  pk=None):
        account_emergency_contact = AccountEmergencyContact.objects.filter(account_id=pk).order_by('-created_at')

        page = self.paginate_queryset(account_emergency_contact)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(account_emergency_contact, many=True)
        return Response(serializer.data)

class AccountFilesViewSet(viewsets.ModelViewSet):
    queryset = AccountFiles.objects.all()
    serializer_class = AccountFilesSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', 'post', 'put', 'delete', 'head']
    query = AccountFiles.objects.prefetch_related('account')

    def get_queryset(self):
        self.queryset = self.queryset.filter(account=self.request.user).order_by('-created_at')
        return self.queryset

    # list account files contact for admin
    @action(detail=True, methods=['get'], permission_classes=[permissions.IsAdminUser])
    def lists(self, request,  pk=None):
        account_emergency_contact = AccountFiles.objects.filter(account_id=pk).order_by('-created_at')

        page = self.paginate_queryset(account_emergency_contact)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(account_emergency_contact, many=True)
        return Response(serializer.data)

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

class UserProfileUpload(APIView):
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, format=None):
        serializer = AccountProfileSerializer(data=request.data, instance=request.user)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, format=None):
        account = request.data.get('account')
        if request.user.is_admin:
            user = Account.objects.get(id=account)
            serializer = AccountProfileSerializer(data=request.data, instance=user)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
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
