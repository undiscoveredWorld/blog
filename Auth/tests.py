from django.contrib.auth.models import User
from django.test import TestCase
from django.db import models
from rest_framework.test import APIClient

from Auth.models import get_generator_of_unique_user, create_user, UserWithRoles
from common.tests import (
    CRUDTestCase,
    MethodsForCRUDTestCase
)

unique_user_gen = get_generator_of_unique_user("test")


class MethodsForUsersTest(MethodsForCRUDTestCase):
    @staticmethod
    def get_create_dict() -> dict:
        return dict(username="test", password="<PASSWORD>", email="test@mail.ru")

    @staticmethod
    def get_list_to_try_change() -> list[dict[str, any]]:
        list_to_try_change: list[dict[str, any]] = [
            {"username": "updated"},
            {"username": "updated", "password": "<PASSWORD>"},
            {"email": "some_email@mail.ru"}
        ]
        return list_to_try_change

    @staticmethod
    def create_instance(**kwargs) -> models.Model:
        return unique_user_gen()

    @staticmethod
    def return_instance_as_dict_to_request(user: User) -> dict[str, any]:
        return {
            "username": user.username,
            "password": user.password,
            "email": user.email
        }


class UsersTest(CRUDTestCase):
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
