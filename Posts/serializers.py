import re

from django.contrib.auth.models import User
from rest_framework import serializers

from Auth.models import UserWithRoles
from Auth.enums import Role
from Posts import models


class PostSerializer(serializers.ModelSerializer):
    def validate_owner(self, owner: User):
        return self._check_user_can_be_owner(owner)

    @staticmethod
    def _check_user_can_be_owner(user: User):
        """Check user can be owner.

        :param user: user to check
        :raises serializers.ValidationError: If user can't be owner
        :returns: user from param user
        """
        user_roles = UserWithRoles.objects.get(user=user)
        if Role.WRITER in user_roles.roles or \
                Role.ADMIN in user_roles.roles or \
                Role.SUPERUSER in user_roles.roles:
            return user
        else:
            raise serializers.ValidationError(f"{user} cannot own any post")

    @staticmethod
    def validate_title(value: str):
        pattern = re.compile(r"^[a-zA-Z0-9 ,._-]{3,}$")
        if not pattern.match(value):
            raise serializers.ValidationError("Invalid title")
        return value

    @staticmethod
    def validate_rating(value: float):
        if value < 0 or value > 10:
            raise serializers.ValidationError("Rating must be between 0 and 10")
        return round(value, 2)

    class Meta:
        fields = '__all__'
        model = models.Post


class BodySerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = models.Body
