from rest_framework import serializers
from django.core.exceptions import ValidationError
from django.db.models import Q
from accounts.models import Account, AccountOtherInformation, AccountEducation, AccountEmergencyContact, AccountFiles
from accounts.utils import create_token
from authServer.keycloak import add_new_user_keycloak
from master.serializers import FilesSerializer
from master.models import Files

class AccountSerializer(serializers.ModelSerializer):
    fullname = serializers.SerializerMethodField('get_full_name_')
    is_staff = serializers.SerializerMethodField('get_status_')
    age = serializers.SerializerMethodField('get_years_birthday_')
    photo = serializers.SerializerMethodField('get_photo_')

    def create(self, validated_data):
        """
        Create and return a new `Snippet` instance, given the validated data.
        """
        try:
            add_new_user_keycloak(validated_data)
        except:
            pass

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
            'marital_status',
            'religion',
            'blood_type',
            'gender',
            'age',
            'telephone',
            'is_staff',
            'id_divisi',
            'divisi',
            'id_jabatan',
            'address',
            'jabatan',
            'photo',
            'manager_category',
            'join_date',
            'is_admin',
            'is_active',
            'resign_date',
            'menu',
            'npwp',
            'bank_account_number',
            'bank_branch',
            'reason_resignation'
        )

    def get_full_name_(self, obj):
        return obj.get_full_name()

    def get_status_(self, obj):
        return obj.is_staff()

    def get_years_birthday_(self, obj):
        return obj.get_years_birthday()
    
    def get_photo_(self, obj):
        if obj.photo:
            return str(obj.get_photo())
        return '#'
        
class AccountOtherInformationSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccountOtherInformation
        fields = '__all__'

class AccountProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ('photo',)

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

class AccountEducationSerializer(serializers.ModelSerializer):
    file = FilesSerializer(required=False)

    def create(self, validated_data):
        """
        Create and return a new `Snippet` instance, given the validated data.
        """     
        file = validated_data.pop('file')
        files = Files.objects.create(**file)
        return AccountEducation.objects.create(file=files, **validated_data)

    def update(self, instance, validated_data):
        """
        Update and return a new `Snippet` instance, given the validated data.
        """    
        if 'file' in validated_data:
            file = validated_data.pop('file')
            nested_serializer = self.fields['file']
            nested_instance = instance.file
            nested_serializer.update(nested_instance, file)
        return super(AccountEducationSerializer, self).update(instance, validated_data)
 
    class Meta:
        model = AccountEducation
        fields = (
            'id',
            'account',
            'name_educational_institution',
            'education_degree',
            'educational_level',
            'graduation_year',
            'majors',
            'file'
        )
    
    def get_file(self, obj):
        return obj.get_file()

class AccountEmergencyContactSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        """
        Create and return a new `Snippet` instance, given the validated data.
        """
        return AccountEmergencyContact.objects.create(**validated_data)

    class Meta:
        model = AccountEmergencyContact
        fields = (
            'id',
            'account',
            'emergency_contact_name',
            'relationship_emergency_contacts',
            'emergency_contact_number'
        )

class AccountFilesSerializer(serializers.ModelSerializer):
    file = FilesSerializer(required=False)

    def create(self, validated_data):
        """
        Create and return a new `Snippet` instance, given the validated data.
        """     
        file = validated_data.pop('file')
        files = Files.objects.create(**file)
        return AccountFiles.objects.create(file=files, **validated_data)

    def update(self, instance, validated_data):
        """
        Update and return a new `Snippet` instance, given the validated data.
        """    
        if 'file' in validated_data:
            file = validated_data.pop('file')
            nested_serializer = self.fields['file']
            nested_instance = instance.file
            nested_serializer.update(nested_instance, file)
        return super(AccountFilesSerializer, self).update(instance, validated_data)
 
    class Meta:
        model = AccountFiles
        fields = (
            'id',
            'account',
            'file'
        )
    
    def get_file(self, obj):
        return obj.get_file()