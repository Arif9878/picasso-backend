from rest_framework import serializers
from django.contrib.auth.models import Permission
from django.core.exceptions import ValidationError
from rest_framework.authtoken.models import Token
from django.db.models import Q
from .models import Account
from .utils import create_token
from authServer.keycloak import add_new_user_keycloak
class AccountSerializer(serializers.ModelSerializer):
    fullname = serializers.SerializerMethodField('get_full_name_')
    is_staff = serializers.SerializerMethodField('get_status_')

    def create(self, validated_data):
        """
        Create and return a new `Snippet` instance, given the validated data.
        """
        add_new_user_keycloak(validated_data)
        return Account.objects.create(**validated_data)
    class Meta:
        model = Account
        fields = (
            'id',
            'email',
            'fullname',
            'username',
            'first_name',
            'last_name',
            'birth_place',
            'birth_date',
            'telephone',
            'is_staff',
            'photo',
            'id_divisi',
            'divisi',
            'id_jabatan',
            'address',
            'jabatan',
            'manager_category',
            'join_date',
            'is_admin',
            'is_active',
            'resign_date',
            'menu',
            'reason_resignation'
        )

    def get_full_name_(self, obj):
        return obj.get_full_name()

    def get_status_(self, obj):
        return obj.is_staff()

class AccountClientAppSerializer(serializers.ModelSerializer):
    fullname = serializers.SerializerMethodField('get_full_name_')

    def create(self, validated_data):
        """
        Create and return a new `Snippet` instance, given the validated data.
        """
        add_new_user_keycloak(validated_data)
        return Account.objects.create(**validated_data)
    class Meta:
        model = Account
        fields = (
            'id',
            'email',
            'fullname',
            'username',
            'birth_place',
            'birth_date',
            'telephone',
            'photo',
            'divisi',
            'address',
            'jabatan',
            'manager_category',
            'join_date',
            'is_active',
            'resign_date'
        )

    def get_full_name_(self, obj):
        return obj.get_full_name()

class AccountLoginSerializer(serializers.HyperlinkedModelSerializer):
    user_obj = None
    token = serializers.CharField(allow_blank=True,read_only=True)
    username = serializers.CharField()
    password = serializers.CharField(style={'input_type': 'password'})

    class Meta:
        model = Account
        fields = ('username','password','email','token')
        extra_kwargs = {'password':
                            {'write_only': True},
                            }

    def validate(self, data):
        username = data.get("username", None)
        password = data["password"]
        if not username:
            raise ValidationError("Username/Email harus di isi")

        user = Account.objects.filter(Q(username=username)|Q(email=username)).distinct()
        if user.exists() and user.count() == 1:
            user_obj = user.first()
        else:
            raise ValidationError("Username/Email yang anda masukkan tidak terdaftar")
        if user_obj:
            if not user_obj.check_password(password):
                raise ValidationError("Password yang anda masukkan salah")
            token = create_token(user_obj)

        data["email"] = user_obj.email
        data["token"] = token
        return data
