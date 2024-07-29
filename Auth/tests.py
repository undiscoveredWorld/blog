from django.contrib.auth.models import User
from django.test import TestCase
from django.db import models
from rest_framework.test import APIClient

from Auth.models import UserWithRoles
from Auth.test_utils import (
    create_user,
    create_unique_user,
    generate_dict_to_request_to_create_unique_user,
)
from common.tests import (
    TestCRUDMixin,
    MethodsForCRUDTestCase,
    TestUniqueValidationMixin,
    TestInvalidInputValidationMixin
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


class RolesTestCase(TestCase):
    give_role_path: str = "/give_role/"
    revoke_role_path: str = "/revoke_role/"

    def test_give_role(self):
        client = APIClient()
        user = create_user()
        response = client.post(f"{self.give_role_path}{user.id}", data={"role": "writer"})
        roles = UserWithRoles.objects.get(user=user)
        self.assertEqual(200, response.status_code)
        self.assertEqual(["writer"], roles.roles)

    def test_give_role_twice(self):
        client = APIClient()
        user = create_user()
        client.post(f"{self.give_role_path}{user.id}", data={"role": "writer"})
        response = client.post(f"{self.give_role_path}{user.id}", data={"role": "writer"})
        roles = UserWithRoles.objects.get(user=user)
        self.assertEqual(200, response.status_code)
        self.assertEqual(["writer"], roles.roles)

    def test_give_invalid_role(self):
        client = APIClient()
        user = create_user()
        response = client.post(f"{self.give_role_path}{user.id}", data={"role": "invalid"})
        self.assertEqual(400, response.status_code)

    def test_request_to_give_role_without_data(self):
        client = APIClient()
        user = create_user()
        response = client.post(f"{self.give_role_path}{user.id}")
        self.assertEqual(400, response.status_code)

    def test_revoke_role(self):
        client = APIClient()
        user = create_user()
        client.post(f"{self.revoke_role_path}{user.id}", data={"role": "writer"})
        response = client.post(f"{self.revoke_role_path}{user.id}", data={"role": "writer"})
        roles = UserWithRoles.objects.get(user=user)
        self.assertEqual(200, response.status_code)
        self.assertEqual([], roles.roles)

    def test_revoke_not_given_role(self):
        client = APIClient()
        user = create_user()
        response = client.post(f"{self.revoke_role_path}{user.id}", data={"role": "writer"})
        roles = UserWithRoles.objects.get(user=user)
        self.assertEqual(200, response.status_code)
        self.assertEqual([], roles.roles)

    def test_revoke_invalid_role(self):
        client = APIClient()
        user = create_user()
        response = client.post(f"{self.revoke_role_path}{user.id}", data={"role": "invalid"})
        self.assertEqual(400, response.status_code)

    def test_request_to_revoke_role_without_data(self):
        client = APIClient()
        user = create_user()
        response = client.post(f"{self.revoke_role_path}{user.id}")
        self.assertEqual(400, response.status_code)


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
    def generate_unique_dict(**kwargs):
        return generate_dict_to_request_to_create_unique_user(**kwargs)

    @staticmethod
    def clear_instances():
        pass

