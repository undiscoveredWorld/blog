from django.db import models
from django.test import TestCase
from rest_framework.test import APIClient

from Auth.enums import Role
from common.tests import (
    TestCRUDMixin,
    MethodsForCRUDTestCase,
    TestUniqueValidationMixin,
    TestInvalidInputValidationMixin,
)
from .models import (
    Body,
    Post,
)
from Auth.test_utils import (
    create_user,
    create_unique_user,
    give_role,
)


class MethodsForPostsTest(MethodsForCRUDTestCase):
    @staticmethod
    def get_create_dict() -> dict:
        body = MethodsForBodiesTest.create_instance()
        user = create_unique_user()
        give_role(user, Role.WRITER)
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
        user = create_user(username="unique-username")
        give_role(user, Role.WRITER)
        body = MethodsForBodiesTest.create_instance()
        list_to_try_change: list[dict[str, any]] = [
            {"owner": user.id},
            {"body": body.id},
            {"owner": user.id, "body": body.id},
            {"title": "Updated"},
            {"is_restricted": True},
            {"rating": 10}
        ]
        return list_to_try_change

    @staticmethod
    def create_instance(**kwargs) -> models.Model:
        body = Body.objects.create(text="Test text")
        user = create_unique_user()
        give_role(user, Role.WRITER)
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


class PostsTestCase(TestCase, TestCRUDMixin):
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


class BodiesTestCase(TestCase, TestCRUDMixin):
    path: str = "/bodies/"
    instance_class: type[models.Model] = Body
    methods: type[MethodsForCRUDTestCase] = MethodsForBodiesTest


class PostsValidationTestCase(TestCase,
                              TestUniqueValidationMixin,
                              TestInvalidInputValidationMixin):
    to_test_unique: dict[str, any] = {
        "title": "Test title",
    }
    path: str = "/posts/"
    to_test_invalid: dict[str, list[any]] = {
        "title": ["", "a", 4, "aa", "aaa+", "a"*51],
        "body": ["sdf"],
        "owner": ["sdf"],
        "is_restricted": ["sdf"],
        "rating": [-1, 11, 100, "sdf"]
    }
    to_test_valid: dict[str, list[any]] = {
        "title": ["test title", "Test title", "Test2 title", "Test,title", "Tset.",
                  "tse_t", "sdf-f"],
        "is_restricted": [True, False],
        "rating": [1, 5, 6.4, 9.234]
    }

    def test_unique_validation(self):
        body = MethodsForBodiesTest.create_instance()
        self.to_test_unique["body"] = body.id

        super().test_unique_validation()

    def test_invalid_input_validation(self):
        body = MethodsForBodiesTest.create_instance()
        owner = create_unique_user()
        give_role(owner, Role.WRITER)
        user = create_unique_user()
        self.to_test_valid["body"] = [body.id]
        self.to_test_valid["owner"] = [owner.id]
        self.to_test_invalid["owner"].append(user.id)
        super().test_invalid_input_validation()

    def test_rating_format(self):
        client = APIClient()
        response = client.post(self.path, self.generate_unique_dict(rating=5.5532345))
        post = Post.objects.get(id=response.data["id"])
        self.assertEqual(5.55, post.rating)

    @staticmethod
    def clear_instances():
        Post.objects.all().delete()

    @staticmethod
    def generate_unique_dict(**kwargs) -> dict[str, any]:
        create_dict = MethodsForPostsTest.get_create_dict()
        return {**create_dict, **kwargs}
