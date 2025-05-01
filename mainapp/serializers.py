from rest_framework import serializers
from .models import CreateEmailTemplate, EmailTag


class EmailFormSerializer(serializers.Serializer):
    Email_From = serializers.EmailField()
    Email_To = serializers.EmailField()
    Email_Type = serializers.CharField(max_length=100)
    Parameters = serializers.CharField()  # String format: <<name>>|John$$<<age>>|30


class CreateEmailTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CreateEmailTemplate
        fields = '__all__'


class EmailTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailTag
        fields = ["name"]






from rest_framework import serializers
from .models import Resume

  
class ResumeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resume
        fields = '__all__'
        
        
