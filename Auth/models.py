from django.db import models
from django.contrib.auth.models import User
from django.contrib.postgres.fields import ArrayField

from . import enums


class UserWithRoles(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    roles = ArrayField(models.CharField(
        choices=enums.Role.choices
    ), default=list)
