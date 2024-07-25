from abc import ABC, abstractmethod
from django.test import TestCase
from django.db import models

from rest_framework.response import Response
from rest_framework.test import APIClient


class MethodsForCRUDTestCase(ABC):
    """This class joins methods needs for CRUD test."""

    @staticmethod
    @abstractmethod
    def get_create_dict() -> dict:
        """Get create dict for request.

        Uses for test_create only

        Returns:
             dict for creation instance in request body like view
        """
        pass

    @staticmethod
    @abstractmethod
    def get_list_to_try_change() -> list[dict[str, any]]:
        """Get list of attributes for trying change it in instance via request.

        Uses for test_update only

        Returns:
            list of attributes of instance to be updated in request body. View of it must be like request body.
        """

        pass

    @staticmethod
    @abstractmethod
    def create_instance(**kwargs) -> models.Model:
        """Create and return instance for test.

        Method must be reusable. All unique fields must be redefined by each call

        Returns:
            instance
        """
        pass

    @staticmethod
    @abstractmethod
    def return_instance_as_dict_to_request(instance: models.Model) -> dict[str, any]:
        """Serialize instance to request and return it."""
        pass


class CRUDTestCase(TestCase):
    path: str
    methods: type[MethodsForCRUDTestCase]
    instance_class: type[models.Model]

    def test_create(self):
        create_dict = self.methods.get_create_dict()
        client = APIClient()
        response: Response = client.post(self.path, create_dict)
        self._test_create_response(response)

    def _test_create_response(self, response: Response) -> None:
        self.assertEqual(201, response.status_code)
        self.assertEqual(1, len(response.data.keys()))
        self.assertTrue("id" in response.data.keys())
        self.assertTrue(type(response.data["id"]) is int)

    def test_update(self):
        list_to_try_change: list[dict[str, any]] = self.methods.get_list_to_try_change()
        self._test_list_to_try_change(list_to_try_change)

    def _test_list_to_try_change(self, list_to_try_change: list[dict[str, any]]):
        client = APIClient()
        for case in list_to_try_change:
            instance = self.methods.create_instance()
            dict_request = {**case}
            response: Response = client.patch(f"{self.path}{instance.id}/", dict_request)
            self.assertEqual(200, response.status_code)
            for key, value in case.items():
                instance_to_check = self.instance_class.objects.get(id=instance.id)
                instance_to_check_dict = self.methods.return_instance_as_dict_to_request(instance_to_check)
                self.assertEqual(value, instance_to_check_dict[key])
            self.instance_class.objects.all().delete()

    def test_delete(self):
        instance = self.methods.create_instance()
        client = APIClient()
        response: Response = client.delete(f"{self.path}{instance.id}/")
        self.assertEqual(204, response.status_code)
        self.assertEqual(0, len(self.instance_class.objects.all()))

    def test_get_one(self):
        instance = self.methods.create_instance()
        client = APIClient()
        response: Response = client.get(f"{self.path}{instance.id}/")
        self.assertEqual(200, response.status_code)

    def test_get_all(self):
        self.methods.create_instance()
        self.methods.create_instance()
        client = APIClient()
        response: Response = client.get(f"{self.path}")
        self.assertEqual(200, response.status_code)
        self.assertEqual(2, len(response.data))
