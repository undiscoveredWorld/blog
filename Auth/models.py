from django.db import models
from django.contrib.auth.models import User
from django.contrib.postgres.fields import ArrayField

from . import enums


class UserWithRoles(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    roles = ArrayField(models.CharField(
        choices=enums.Role.choices
    ), default=list)


prefixes = set()


def get_generator_of_unique_user(prefix: str) -> (callable or None):
    """Get function that generates unique user.

    Returns:
        gen_user() -> User
    """
    if prefix in prefixes:
        return
    prefixes.add(prefix)
    i = 0

    def gen_user() -> User:
        nonlocal prefix, i
        username = f"{prefix}-{i}"
        i += 1
        return create_user(username=username)

    return gen_user


def create_user(**kwargs):
    default_attrs = {"username": "test", "password": "00", "email": "test@mail.ru"}
    kwargs_for_user = {**default_attrs, **kwargs}
    user: User = User.objects.create_user(**kwargs_for_user)
    UserWithRoles.objects.create(user=user, roles=[])
    return user
