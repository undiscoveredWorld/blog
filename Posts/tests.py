from django.db import models

from common.tests import (
    CRUDTestCase,
    MethodsForCRUDTestCase,
)
from .models import (
    Body,
    Post,
)
from Auth.models import get_generator_of_unique_user, create_user

unique_user_gen = get_generator_of_unique_user("user")


class MethodsForPostsTest(MethodsForCRUDTestCase):

    @staticmethod
    def get_create_dict() -> dict:
        body = MethodsForBodiesTest.create_instance()
        user = unique_user_gen()
        create_dict = {
            "owner": user.id,
            "body": body.id,
            "title": "Test title",
            "is_restricted": False,
            "rating": 0,
        }
        return create_dict

    @staticmethod
    def get_list_to_try_change() -> list[dict[str, any]]:
        user = create_user(username="unique username")
        body = MethodsForBodiesTest.create_instance()
        list_to_try_change: list[dict[str, any]] = [
            {"owner": user.id},
            {"body": body.id},
            {"owner": user.id, "body": body.id},
            {"title": "Updated"},
            {"is_restricted": True},
            {"rating": 100}
        ]
        return list_to_try_change

    @staticmethod
    def create_instance(**kwargs) -> models.Model:
        body = Body.objects.create(text="Test text")
        user = unique_user_gen()
        default_attrs = {
            "owner": user,
            "body": body,
            "title": "Test title",
            "is_restricted": False,
            "rating": 0,
        }

        kwargs_for_post = {**default_attrs, **kwargs}
        post: Post = Post.objects.create(**kwargs_for_post)
        return post

    @staticmethod
    def return_instance_as_dict_to_request(post: Post) -> dict[str, any]:
        return {
            "owner": post.owner.id,
            "body": post.body.id,
            "title": post.title,
            "rating": post.rating,
            "is_restricted": post.is_restricted,
        }


class PostsTestCase(CRUDTestCase):
    path: str = "/posts/"
    methods: type[MethodsForCRUDTestCase] = MethodsForPostsTest
    instance_class: type[models.Model] = Post


class MethodsForBodiesTest(MethodsForCRUDTestCase):
    @staticmethod
    def get_create_dict() -> dict:
        create_dict = {
            "text": "Test text"
        }
        return create_dict

    @staticmethod
    def get_list_to_try_change() -> list[dict[str, any]]:
        list_to_try_change: list[dict[str, any]] = [
            {"text": "Updated text"}
        ]
        return list_to_try_change

    @staticmethod
    def create_instance(**kwargs) -> models.Model:
        default_attrs = {
            "text": "Test text"
        }

        kwargs_for_body = {**default_attrs, **kwargs}
        body: Body = Body.objects.create(**kwargs_for_body)
        return body

    @staticmethod
    def return_instance_as_dict_to_request(body: Body) -> dict[str, any]:
        return {
            "text": body.text
        }


class BodiesTestCase(CRUDTestCase):
    path: str = "/bodies/"
    instance_class: type[models.Model] = Body
    methods: type[MethodsForCRUDTestCase] = MethodsForBodiesTest
