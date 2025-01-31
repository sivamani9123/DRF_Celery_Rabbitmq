from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import serializers
from .models import DatabaseCredential, User

class DatabaseCredentialSerializer(serializers.ModelSerializer):
    class Meta:
        model = DatabaseCredential
        fields = '__all__'

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    
    
class UserSignupSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [ 'username', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data['password'])  # Hash password
        user = User.objects.create(**validated_data)
        return user
