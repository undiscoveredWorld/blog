from django.contrib.auth.models import User
from rest_framework.test import APIClient

from Auth.enums import Role
from Auth.models import UserSerializer, UserWithRoles

prefix = "test-user"
i = 0


def generate_username() -> str:
    """Generate a unique username.

    Uses global variables 'prefix and 'i'.
    """
    global i, prefix
    i += 1
    return f"{prefix}-{i}"


def generate_dict_to_request_to_create_unique_user(**kwargs) -> dict[str, any]:
    """Generate a dictionary to creation a unique user via request.

    :param kwargs: rewrites unique and default values for result user
    """
    username = generate_username()
    email = f"{username}@mail.ru"
    return {"username": username, "email": email, "password": "<PasSWORD1>", **kwargs}


def create_user(**kwargs) -> User:
    """Create not unique user.

    Side effect: creates a new UserWithRoles to new user.
    :param kwargs: rewrites default values for result user
    """
    default_attrs = {"username": "test", "password": "<PasSWORD1>", "email": "test@mail.ru"}
    kwargs_for_user = {**default_attrs, **kwargs}
    user = _create_user_with_serializer(kwargs_for_user)
    UserWithRoles.objects.create(user=user, roles=[])
    return user


def _create_user_with_serializer(kwargs_for_user) -> User:
    serializer = UserSerializer(data=kwargs_for_user)
    serializer.is_valid(raise_exception=True)
    user = serializer.save()
    return user


def create_unique_user(**kwargs):
    """Create unique user.

    Side effect: creates a new UserWithRoles to new user.
    :param kwargs: rewrites unique and default values for result user
    """
    attrs = generate_dict_to_request_to_create_unique_user(**kwargs)
    return create_user(**attrs)


def give_role(user: User, role: Role) -> list[Role]:
    user_with_roles = UserWithRoles.objects.get(user=user)
    if role not in user_with_roles.roles:
        user_with_roles.roles.append(role)
        user_with_roles.save()
    return user_with_roles.roles


def create_or_get_superuser() -> User:
    if User.objects.filter(username="superU").exists():
        return User.objects.get(username="superU")
    else:
        user: User = create_unique_user(username="superU")
        user.is_superuser = True
        user.save()
        give_role(user, Role.SUPERUSER)
        return user


def get_superuser_client(**kwargs) -> APIClient:
    su = create_or_get_superuser()
    client = APIClient()
    client.force_authenticate(user=su)
    return client
