from rest_framework import serializers
from .models import Files

class FilesSerializer(serializers.ModelSerializer):
    file = serializers.FileField(required=False, allow_null=True)

    def create(self, validated_data):
        """
        Create and return a new `Snippet` instance, given the validated data.
        """
        return Files.objects.create(**validated_data)
    
    class Meta:
        model = Files
        fields = (
            'file_name',
            'file_number',
            'file',
            'note'
        )
