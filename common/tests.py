from abc import ABC, abstractmethod
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


class TestCRUDMixin:
    """Mixin extends TestCase by CRUD tests.

    Variables:
        :var path: to api view to test. Must ends by '/'
    """
    path: str
    methods: type[MethodsForCRUDTestCase]
    instance_class: type[models.Model]

    def test_create(self):
        create_dict = self.methods.get_create_dict()
        client = APIClient()
        response: Response = client.post(self.path, create_dict)
        self._test_create_response(response)

    def _test_create_response(self, response: Response) -> None:
        self.assertEqual(201, response.status_code,
                         msg=f"Expected invalid code.\n"
                             f"Details: {response.data}")
        self.assertEqual(1, len(response.data.keys()),
                         msg=f"Too much fields: expected 1, got {len(response.data.keys())}")
        self.assertTrue("id" in response.data.keys(),
                        msg=f"'id' field is missing in response")
        self.assertTrue(type(response.data["id"]) is int,
                        msg=f"'id' field must be int")

    def test_update(self):
        list_to_try_change: list[dict[str, any]] = self.methods.get_list_to_try_change()
        self._test_list_to_try_change(list_to_try_change)

    def _test_list_to_try_change(self, list_to_try_change: list[dict[str, any]]):
        client = APIClient()
        for case in list_to_try_change:
            instance = self.methods.create_instance()
            dict_request = {**case}
            response: Response = client.patch(f"{self.path}{instance.id}/", dict_request)
            self.assertEqual(200, response.status_code,
                             msg=f"Cannot update instance in the case {case}.\n"
                                 f"Detail: {response.data}")
            for key, value in case.items():
                instance_to_check = self.instance_class.objects.get(id=instance.id)
                instance_to_check_dict = self.methods.return_instance_as_dict_to_request(instance_to_check)
                self.assertEqual(value, instance_to_check_dict[key],
                                 msg=f"Request updated instance invalid or response is invalid.\n"
                                     f"Expected: {instance_to_check_dict[key]}, Received: {value}. Field: {key}")
            self.instance_class.objects.all().delete()

    def test_delete(self):
        instance = self.methods.create_instance()
        client = APIClient()
        response: Response = client.delete(f"{self.path}{instance.id}/")
        self.assertEqual(204, response.status_code,
                         msg=f"Cannot delete instance.\n"
                             f"Details: {response.data}")
        self.assertEqual(0, len(self.instance_class.objects.all()),
                         msg=f"Request is successful, but instance were not deleted")

    def test_get_one(self):
        instance = self.methods.create_instance()
        client = APIClient()
        response: Response = client.get(f"{self.path}{instance.id}/")
        self.assertEqual(200, response.status_code,
                         msg=f"Cannot get one instance by id {instance.id}.\n"
                             f"Details: {response.data}")

    def test_get_all(self):
        self.methods.create_instance()
        self.methods.create_instance()
        client = APIClient()
        response: Response = client.get(f"{self.path}")
        self.assertEqual(200, response.status_code,
                         msg=f"Cannot get all instances."
                             f"Details: {response.data}")
        self.assertEqual(2, len(response.data),
                         msg=f"Response contains invalid count of instances")


class TestValidationMixin(ABC):
    """Abstract class for validation tests mixins.

    :var path: to api view to test. Must ends by '/'
    """
    path: str

    @staticmethod
    @abstractmethod
    def generate_unique_dict(**kwargs) -> dict[str, any]:
        """Return dict to multipy creating of instances.

        :arg kwargs: Attributes for instance, that will be applied to instance over default
        """
        pass


class TestUniqueValidationMixin(TestValidationMixin, ABC):
    """Mixin for validation of unique tests.

    :var to_test_unique: dict, where keys are field names and values are a values, with that create instance is possibly
    """
    to_test_unique: dict[str, any]

    def test_unique_validation(self):
        client = APIClient()
        for key, value in self.to_test_unique.items():
            to_create_request = self.generate_unique_dict(**{key: value})
            response = client.post(f"{self.path}", data=to_create_request)
            self.assertEqual(201, response.status_code,
                             msg=f"Cannot create first instance(unique)\n"
                                 f"Details: {response.data}.\n"
                                 f"Case: {key}:{value}")
            response = client.post(f"{self.path}", data=to_create_request)
            self.assertEqual(400, response.status_code,
                             msg=f"Created not unique instance."
                                 f"Case: {key}:{value}")


class TestInvalidInputValidationMixin(TestValidationMixin, ABC):
    """Mixin for validation of invalid/valid input tests.

    :var to_test_invalid: dict, where keys are field names and values are lists of invalid field values
    :var to_test_valid: dict, where keys are field names and values are lists of valid field values
    """
    to_test_invalid: dict[str, list[any]]
    to_test_valid: dict[str, list[any]]

    def test_invalid_input_validation(self):
        self._test_items(dictionary=self.to_test_invalid, expected_code=400,
                         get_msg=self._get_invalid_test_assertion_msg)
        self._test_items(dictionary=self.to_test_valid, expected_code=201,
                         get_msg=self._get_valid_test_assertion_msg)

    def _test_items(self, dictionary: dict[str, list[str]],
                    expected_code: int, get_msg: callable) -> None:
        client: APIClient = APIClient()
        for key, values_list in dictionary.items():
            for value in values_list:
                to_create_request = self.generate_unique_dict(**{key: value})
                response = client.post(f"{self.path}", data=to_create_request)

                msg = get_msg(value=value, field=key)
                self.assertEqual(expected_code, response.status_code, msg=msg)

    @staticmethod
    def _get_invalid_test_assertion_msg(value: str, field: str):
        return f"Accepted invalid value '{value}' for {field} field"

    @staticmethod
    def _get_valid_test_assertion_msg(value: str, field: str):
        return f"Did not accepted valid value '{value}' for {field} field"
