import re

from django.db import models
from django.contrib.auth.models import User
from django.contrib.postgres.fields import ArrayField
from rest_framework import serializers

from . import enums, validators


class UserWithRoles(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    roles = ArrayField(models.CharField(
        choices=enums.Role.choices
    ), default=list)


class UserSerializer(serializers.ModelSerializer):
    @staticmethod
    def validate_username(value):
        # username contains from 3 to 20 word symbols or number symbols or _ or -
        pattern = re.compile('^[a-zA-Z0-9_-]{3,20}$')
        if not pattern.match(value):
            raise serializers.ValidationError("Username is invalid")
        return value

    @staticmethod
    def validate_password(value):
        return validators.validate_password(value)

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

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'id')
        extra_kwargs = {'email': {'required': True}}


class UserUpdateSerializer(serializers.ModelSerializer):
    def validate_password(self, value):
        return validators.validate_password(value)

    class Meta:
        model = User
        fields = ('password',)


class UserWithRolesSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserWithRoles
        fields = ('user', 'roles')


class RoleRequest(models.Model):
    date = models.DateField(auto_now_add=True, null=False, blank=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False, blank=False)
    expected_role = models.CharField(choices=enums.Role.choices, null=False, blank=False, max_length=10)
    status = models.CharField(choices=enums.RoleRequestStatus, null=False, blank=False,
                              default=enums.RoleRequestStatus.OPENED, max_length=10)
    message = models.TextField(blank=True, null=False, default="")


class RoleRequestCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoleRequest
        fields = ('expected_role', 'message', 'user', 'id')


class RoleRequestGetSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoleRequest
        fields = ('expected_role', 'message', 'user', 'id', 'date', 'status')
