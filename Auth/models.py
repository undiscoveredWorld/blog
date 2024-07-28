import re

from django.db import models
from django.contrib.auth.models import User
from django.contrib.postgres.fields import ArrayField
from rest_framework import serializers

from . import enums


class UserWithRoles(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    roles = ArrayField(models.CharField(
        choices=enums.Role.choices
    ), default=list)


class UserSerializer(serializers.ModelSerializer):
    def validate_email(self, value):
        self._check_email_is_unique(value)
        self._check_value_is_email(value)
        return value

    @staticmethod
    def _check_email_is_unique(value):
        queryset = User.objects.all()
        queryset = queryset.filter(email=value)
        if queryset:
            raise serializers.ValidationError("Email must be unique")

    @staticmethod
    def _check_value_is_email(value):
        pattern = re.compile('^[a-zA-Z-_0-9]+@[a-zA-Z-_]+.[a-zA-Z]+$')
        if not pattern.match(value):
            raise serializers.ValidationError("Email is invalid")

    def validate_username(self, value):
        # username contains from 3 to 20 word symbols or number symbols or _ or -
        pattern = re.compile('^[a-zA-Z0-9_-]{3,20}$')
        if not pattern.match(value):
            raise serializers.ValidationError("Username is invalid")
        return value

    def validate_password(self, value):
        # password contains least one symbol lower case, one symbol upper case, one non-word symbol.
        # And length of password more, than 8
        pattern = re.compile(r'^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?\W).{8,}$')
        if not pattern.match(value):
            raise serializers.ValidationError("Password is too week")
        return value

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'id')
        extra_kwargs = {'email': {'required': True}}


class UserWithRolesSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserWithRoles
        fields = ('user', 'roles')
