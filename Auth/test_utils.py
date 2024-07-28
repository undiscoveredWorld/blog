from Auth.models import UserSerializer, UserWithRoles

prefix = "test-user"
i = 0


def gen_username() -> str:
    global i
    i += 1
    return f"{prefix}-{i}"


def generate_dict_to_request_to_create_unique_user(**kwargs) -> dict[str, any]:
    username = gen_username()
    email = f"{username}@mail.ru"
    return {"username": username, "email": email, "password": "<PasSWORD1>", **kwargs}


def create_user(**kwargs):
    default_attrs = {"username": "test", "password": "<PasSWORD1>", "email": "test@mail.ru"}
    kwargs_for_user = {**default_attrs, **kwargs}
    user = _create_user_with_serializer(kwargs_for_user)
    UserWithRoles.objects.create(user=user, roles=[])
    return user


def _create_user_with_serializer(kwargs_for_user):
    serializer = UserSerializer(data=kwargs_for_user)
    serializer.is_valid(raise_exception=True)
    user = serializer.save()
    return user


def create_unique_user(**kwargs):
    attrs = generate_dict_to_request_to_create_unique_user(**kwargs)
    return create_user(**attrs)
