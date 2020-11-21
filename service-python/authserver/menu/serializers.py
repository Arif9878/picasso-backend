from rest_framework import serializers
from .models import Menu, MenuType

class MenuTypeSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        """
        Create and return a new `Snippet` instance, given the validated data.
        """
        return MenuType.objects.create(**validated_data)

    class Meta:
        model = MenuType
        fields = (
            'id',
            'menu_type',
            'description'
        )

class MenuSerializer(serializers.ModelSerializer):
    
    def create(self, validated_data):
        """
        Create and return a new `Snippet` instance, given the validated data.
        """
        return Menu.objects.create(**validated_data)

    class Meta:
        model = Menu
        fields = (
            'id',
            'parent',
            'menu_type',
            'title',
            'icon',
            'furl',
            'seq',
            'enable',
            'permissions'
        )
