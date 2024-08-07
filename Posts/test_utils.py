from Auth.enums import Role
from Auth.test_utils import create_unique_user, give_role
from .models import Body, Post
from .serializers import BodySerializer, PostSerializer


title_prefix = "test_post"
i = 0


def _get_next_unique_title():
    global i, title_prefix
    i += 1
    return f"{title_prefix}{i}"


def get_create_dict_for_body(**kwargs):
    create_dict = {
        "text": "Test text",
        **kwargs
    }
    return create_dict


def get_create_dict_for_post(**kwargs):
    body = create_body()
    user = create_unique_user()
    give_role(user, Role.WRITER)
    create_dict = {
        "owner": user.id,
        "body": body.id,
        "title": _get_next_unique_title(),
        "is_restricted": False,
        "rating": 0,
        **kwargs
    }
    return create_dict


def create_body(**kwargs) -> Body:
    kwargs_for_body = {**get_create_dict_for_body(**kwargs)}
    serializer = BodySerializer(data=kwargs_for_body)
    serializer.is_valid(raise_exception=True)
    return serializer.save()


def create_post(**kwargs) -> Post:
    kwargs_for_post = {**get_create_dict_for_post(**kwargs)}
    serializer = PostSerializer(data=kwargs_for_post)
    serializer.is_valid(raise_exception=True)
    return serializer.save()
