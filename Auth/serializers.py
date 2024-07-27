from rest_framework import serializers
from django.contrib.auth.models import User

from Auth.models import UserWithRoles


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'id')
        extra_kwargs = {'email': {'required': True}}


class UserWithRolesSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserWithRoles
        fields = ('user', 'roles')
