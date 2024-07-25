from django.contrib.auth.models import User
from django.db import models

from Auth.models import get_generator_of_unique_user
from common.tests import (
    CRUDTestCase,
    MethodsForCRUDTestCase
)

unique_user_gen = get_generator_of_unique_user("test")


class MethodsForUsersTest(MethodsForCRUDTestCase):
    @staticmethod
    def get_create_dict() -> dict:
        return dict(username="test", password="<PASSWORD>")

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
