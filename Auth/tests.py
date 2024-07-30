from django.contrib.auth.models import User
from django.test import TestCase
from django.db import models
from rest_framework import status
from rest_framework.response import Response
from rest_framework.test import APIClient

from Auth.enums import Role
from Auth.models import UserWithRoles
from Posts.models import Post, Body
from Auth.test_utils import (
    create_user,
    create_unique_user,
    generate_dict_to_request_to_create_unique_user,
    get_superuser_client,
    give_role,
)
from Posts.serializers import PostSerializer
from common.tests import (
    TestCRUDMixin,
    MethodsForCRUDTestCase,
    TestUniqueValidationMixin,
    TestInvalidInputValidationMixin,
    PermissionTestCaseMixin
)


class MethodsForUsersTest(MethodsForCRUDTestCase):
    @staticmethod
    def get_create_dict() -> dict:
        return generate_dict_to_request_to_create_unique_user()

    @staticmethod
    def get_list_to_try_change() -> list[dict[str, any]]:
        list_to_try_change: list[dict[str, any]] = [
            {"username": "updated"},
            {"username": "updated", "password": "<P0SSWORd>"},
            {"email": "some_email@mail.ru"}
        ]
        return list_to_try_change

    @staticmethod
    def create_instance(**kwargs) -> models.Model:
        return create_unique_user(**kwargs)

    @staticmethod
    def return_instance_as_dict_to_request(user: User) -> dict[str, any]:
        return {
            "username": user.username,
            "password": user.password,
            "email": user.email
        }


class UsersTestCase(TestCase, TestCRUDMixin):
    path: str = "/users/"
    methods: type[MethodsForCRUDTestCase] = MethodsForUsersTest
    instance_class: type[models.Model] = User

    @staticmethod
    def get_client(**kwargs) -> APIClient:
        return get_superuser_client()

    def test_retrieve_user_info(self):
        client = self.get_client()
        user = create_user()
        give_role(user, Role.WRITER)
        body = Body.objects.create(text="Test text")
        post = Post.objects.create(
            owner=user,
            body=body,
            title="Some title",
            is_restricted=False,
            rating=5
        )
        serializer = PostSerializer(post)

        response = client.get(f"{self.path}{user.id}/")
        self.assertEqual(200, response.status_code)
        self.assertEqual({
            "roles": ['writer'],
            "posts": [serializer.data],
            "username": user.username,
            "email": user.email,
            "password": user.password,
            "id": user.id
        }, response.data)


class UsersPermissionsTestCase(TestCase, PermissionTestCaseMixin):
    path: str = "/users/"
    successful_client_getters: dict[str, callable] = {
        "get": [APIClient, get_superuser_client],
        "get_one": [APIClient, get_superuser_client],
        "post": [get_superuser_client],
        "put": [get_superuser_client],
        "patch": [get_superuser_client],
        "delete": [get_superuser_client],
    }
    unsuccessful_client_getters: dict[str, callable] = {
        "post": [APIClient],
        "put": [APIClient],
        "patch": [APIClient],
        "delete": [APIClient],
    }

    def _test_get(self, client: APIClient) -> Response | None:
        return client.get(self.path)

    def _test_get_one(self, client: APIClient) -> Response | None:
        user: User = create_user()
        response = client.get(f"{self.path}{user.id}")
        User.objects.get(id=user.id).delete()
        return response

    def _test_post(self, client: APIClient) -> Response | None:
        create_dict = generate_dict_to_request_to_create_unique_user()
        response = client.post(self.path, data=create_dict)
        if response.status_code == status.HTTP_201_CREATED:
            User.objects.get(username=create_dict["username"]).delete()
        return response

    def _test_patch(self, client: APIClient) -> Response | None:
        user = create_unique_user()
        response = client.patch(f"{self.path}{user.id}",
                                data={"username": "Some unique username"})
        if response.status_code == status.HTTP_200_OK:
            User.objects.get(username="Some unique username").delete()
        else:
            User.objects.get(username=user.username).delete()
        return response

    def _test_put(self, client: APIClient) -> Response | None:
        user = create_unique_user()
        update_dict = generate_dict_to_request_to_create_unique_user()
        response = client.put(f"{self.path}{user.id}", data=update_dict)
        if response.status_code == status.HTTP_200_OK:
            User.objects.get(username=update_dict["username"]).delete()
        else:
            User.objects.get(username=user.username).delete()
        return response

    def _test_delete(self, client: APIClient) -> Response | None:
        user = create_unique_user()
        response = client.delete(f"{self.path}{user.id}")
        return response


class RegistrationPermissionTestCase(TestCase, PermissionTestCaseMixin):
    path: str = "/registration/"
    successful_client_getters: dict[str, list[callable]] = {
        "post": [APIClient]
    }
    unsuccessful_client_getters: dict[str, list[callable]] = {}

    def _test_get(self, client: APIClient) -> Response | None:
        pass

    def _test_get_one(self, client: APIClient) -> Response | None:
        pass

    def _test_post(self, client: APIClient) -> Response | None:
        create_dict = generate_dict_to_request_to_create_unique_user()
        response = client.post(self.path, data=create_dict)
        if response.status_code == status.HTTP_201_CREATED:
            User.objects.get(username=create_dict["username"]).delete()
        return response

    def _test_patch(self, client: APIClient) -> Response | None:
        pass

    def _test_put(self, client: APIClient) -> Response | None:
        pass

    def _test_delete(self, client: APIClient) -> Response | None:
        pass


class RolesTestCase(TestCase):
    give_role_path: str = "/give_role/"
    revoke_role_path: str = "/revoke_role/"

    def test_give_role(self):
        client = APIClient()
        user = create_user()
        response = client.post(f"{self.give_role_path}{user.id}", data={"role": "writer"})
        roles = UserWithRoles.objects.get(user=user)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(["writer"], roles.roles)

    def test_give_role_twice(self):
        client = APIClient()
        user = create_user()
        client.post(f"{self.give_role_path}{user.id}", data={"role": "writer"})
        response = client.post(f"{self.give_role_path}{user.id}", data={"role": "writer"})
        roles = UserWithRoles.objects.get(user=user)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(["writer"], roles.roles)

    def test_give_invalid_role(self):
        client = APIClient()
        user = create_user()
        response = client.post(f"{self.give_role_path}{user.id}", data={"role": "invalid"})
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

    def test_request_to_give_role_without_data(self):
        client = APIClient()
        user = create_user()
        response = client.post(f"{self.give_role_path}{user.id}")
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

    def test_revoke_role(self):
        client = APIClient()
        user = create_user()
        client.post(f"{self.revoke_role_path}{user.id}", data={"role": "writer"})
        response = client.post(f"{self.revoke_role_path}{user.id}", data={"role": "writer"})
        roles = UserWithRoles.objects.get(user=user)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual([], roles.roles)

    def test_revoke_not_given_role(self):
        client = APIClient()
        user = create_user()
        response = client.post(f"{self.revoke_role_path}{user.id}", data={"role": "writer"})
        roles = UserWithRoles.objects.get(user=user)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual([], roles.roles)

    def test_revoke_invalid_role(self):
        client = APIClient()
        user = create_user()
        response = client.post(f"{self.revoke_role_path}{user.id}", data={"role": "invalid"})
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

    def test_request_to_revoke_role_without_data(self):
        client = APIClient()
        user = create_user()
        response = client.post(f"{self.revoke_role_path}{user.id}")
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)


class UsersValidationTestCase(TestCase,
                              TestUniqueValidationMixin,
                              TestInvalidInputValidationMixin):
    path: str = "/users/"
    to_test_unique = {"username": "not_unique", "email": "not_unique@mail.ru"}
    to_test_invalid = {
        "username": ["", "a", "aa", "test@", "test$", "test+", "tset=", "t" * 21, "te st"],
        "email": ["", "a", "a@", "a$mail.ru", "a@mail", "a+@mail.ru", "a@mail.r-u"],
        "password": ["", *{"a" * i for i in range(8)}, "password", "passworD", "<P0SSWORD>"]
    }
    to_test_valid = {
        "username": ["aaa", "aaa4", "aaa_aaa", "aaa-aaa", "a" * 20],
        "email": ["a@mail.ru", "a" * 100 + "@mail.ru"],
        "password": ["aaaaaaA7<", "aфффффффффA7<"]
    }

    @staticmethod
    def get_client(**kwargs) -> APIClient:
        return get_superuser_client()

    @staticmethod
    def generate_unique_dict(**kwargs):
        return generate_dict_to_request_to_create_unique_user(**kwargs)

    @staticmethod
    def clear_instances():
        pass


class RegistrationUserTestCase(TestCase):
    path: str = "/registration/"

    def test_register_user(self):
        client = APIClient()
        username = "test"
        response = client.post(self.path, {
            "username": username,
            "email": f"{username}@mail.ru",
            "password": "<P0SSWOrD>"
        })
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        user = User.objects.get(id=response.data["id"])
        self.assertEqual(username, user.username)

    def test_end_point_have_post_method_only(self):
        client = APIClient()
        response = client.get(self.path)
        self.assertEqual(status.HTTP_405_METHOD_NOT_ALLOWED, response.status_code)
        response = client.put(self.path)
        self.assertEqual(status.HTTP_405_METHOD_NOT_ALLOWED, response.status_code)
        response = client.patch(self.path)
        self.assertEqual(status.HTTP_405_METHOD_NOT_ALLOWED, response.status_code)
