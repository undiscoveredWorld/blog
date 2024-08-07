# TODO: unique of pair role and user
from datetime import date

from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework.response import Response

from .enums import Role, RoleRequestStatus
from .models import RoleRequest
from .test_utils import (
    get_superuser_client,
    create_unique_user,
    generate_username,
    generate_dict_to_request_to_create_unique_user,
    give_role, get_authenticated_client, get_admin_client
)
from Posts.test_utils import create_post
from Posts.serializers import PostSerializer
from common.tests import HTTPAsserts


def _get_data_for_validation_test_on_create_user() -> tuple[dict[str, list], dict[str, list]]:
    to_test_invalid: dict[str, list] = {
        "password": ["x" * i for i in range(8)] + [f"{'x' * 8}X"] +
                    [f"{'x' * 8}X1", 121],
        "username": ["x" * i for i in range(3)] + ["xxx+"],
        "email": ["", "x", "x+mail.ru", "x@", "x@mail"]
    }
    to_test_valid: dict[str, list] = {
        "password": [f"{'x' * 8}X1>"],
        "username": ["xxx_", "xxx3", "xxx-", "xxxX", 121],
        "email": ["x@mail.ru"]
    }
    return to_test_invalid, to_test_valid


def _get_data_for_unique_test_user() -> dict[str, any]:
    return {
        "username": "not_unique",
        "email": "not_unique@mail.ru"
    }


class UserTestCase(TestCase, HTTPAsserts):
    path: str = "/users/"

    def test_get_all(self):
        client = get_superuser_client()
        response: Response = client.get(self.path)
        self.assert_http_not_3xx_code(response)
        self.assert_http_200(response)

    def test_get_one(self):
        su_client = get_superuser_client()
        user = create_unique_user()
        response: Response = su_client.get(f"{self.path}{user.id}/")
        self.assert_http_not_3xx_code(response)
        self.assert_http_200(response)

    def test_post(self):
        su_client = get_superuser_client()
        username = generate_username()
        data = {
            "username": username,
            "email": f"{username}@mail.ru",
            "password": "<PaSSW0RD>"
        }
        response: Response = su_client.post(self.path, data=data)
        self.assert_http_not_3xx_code(response)
        self.assert_http_201(response)

    def test_patch(self):
        su_client = get_superuser_client()
        user = create_unique_user()
        data = {
            "password": "<paSSW0RD>"
        }
        response: Response = su_client.patch(f"{self.path}{user.id}/", data=data)
        self.assert_http_not_3xx_code(response)
        self.assert_http_200(response)

    def test_put(self):
        su_client = get_superuser_client()
        user = create_unique_user()
        data = {
            "password": "<paSSW0RD>"
        }
        response: Response = su_client.put(f"{self.path}{user.id}/", data=data)
        self.assert_http_not_3xx_code(response)
        self.assert_http_200(response)

    def test_delete(self):
        su_client = get_superuser_client()
        user = create_unique_user()
        response: Response = su_client.delete(f"{self.path}{user.id}/")
        self.assert_http_not_3xx_code(response)
        self.assert_http_204(response)

    def test_validation_on_update(self):
        to_test_invalid: dict[str, list] = {
            "password": ["x" * i for i in range(8)] + [f"{'x' * 8}X"] +
                        [f"{'x' * 8}X1"]
        }
        to_test_valid: dict[str, list] = {
            "password": [f"{'x' * 8}X1>"]
        }
        self._test_invalid_data_on_update(to_test_invalid)
        self._test_valid_data_on_update(to_test_valid)

    def _test_valid_data_on_update(self, to_test_valid):
        user = create_unique_user()
        su_client = get_superuser_client()
        for field_name, value_list in to_test_valid.items():
            for value in value_list:
                data = {field_name: value}
                response: Response = su_client.patch(f"{self.path}{user.id}/", data=data)
                self.assert_http_not_3xx_code(response)
                self.assert_http_200(response)

    def _test_invalid_data_on_update(self, to_test_invalid):
        user = create_unique_user()
        su_client = get_superuser_client()
        for field_name, value_list in to_test_invalid.items():
            for value in value_list:
                data = {field_name: value}
                response: Response = su_client.patch(f"{self.path}{user.id}/", data=data)
                self.assert_http_not_3xx_code(response)
                self.assert_http_400(response)

    def test_validation_on_create(self):
        to_test_invalid, to_test_valid = _get_data_for_validation_test_on_create_user()
        self._test_invalid_data_on_create(to_test_invalid)
        self._test_valid_data_on_create(to_test_valid)

    def _test_valid_data_on_create(self, to_test_valid):
        su_client = get_superuser_client()
        for field_name, value_list in to_test_valid.items():
            for value in value_list:
                data = generate_dict_to_request_to_create_unique_user(**{field_name: value})
                response: Response = su_client.post(self.path, data=data)
                self.assert_http_not_3xx_code(response)
                self.assert_http_201_with_addition(response, f" Case: {field_name}-{value}")

    def _test_invalid_data_on_create(self, to_test_invalid):
        su_client = get_superuser_client()
        for field_name, value_list in to_test_invalid.items():
            for value in value_list:
                data = generate_dict_to_request_to_create_unique_user(**{field_name: value})
                response: Response = su_client.post(self.path, data=data)
                self.assert_http_not_3xx_code(response)
                self.assert_http_400_with_addition(response, f" Case: {field_name}-{value}")

    def test_unique_on_create(self):
        to_test: dict[str, any] = _get_data_for_unique_test_user()
        su_client = get_superuser_client()
        for field_name, value in to_test.items():
            data = generate_dict_to_request_to_create_unique_user(**{field_name: value})
            response: Response = su_client.post(self.path, data=data)
            self.assert_http_201_with_addition(response, f" Case: {field_name}-{value}")
            response: Response = su_client.post(self.path, data=data)
            self.assert_http_400_with_addition(response, f" Case: {field_name}-{value}")

    def test_who_can_get_all(self):
        to_test = self._get_default_to_test_accession()
        testing_index = 0
        for client in to_test:
            response: Response = client.get(self.path)
            self.assert_http_not_3xx_code(response)
            self.assert_http_provided_access_with_addition(response, f"Case: {testing_index} index fail test")
            testing_index += 1

    def test_who_can_get_one(self):
        to_test = self._get_default_to_test_accession()
        testing_index = 0
        user = create_unique_user()
        for client in to_test:
            response: Response = client.get(f"{self.path}{user.id}/")
            self.assert_http_not_3xx_code(response)
            self.assert_http_provided_access_with_addition(response, f"Case: {testing_index} index fail test")
            testing_index += 1

    def test_who_cannot_post(self):
        to_test = self._get_default_to_test_accession()
        testing_index = 0
        for client in to_test:
            response: Response = client.post(f"{self.path}")
            self.assert_http_not_3xx_code(response)
            self.assert_http_denied_access_with_addition(response, f"Case: {testing_index} index fail test")
            testing_index += 1

    def test_who_cannot_put(self):
        to_test = self._get_default_to_test_accession()
        testing_index = 0
        for client in to_test:
            response: Response = client.put(f"{self.path}")
            self.assert_http_not_3xx_code(response)
            self.assert_http_denied_access_with_addition(response, f"Case: {testing_index} index fail test")
            testing_index += 1

    def test_who_cannot_patch(self):
        to_test = self._get_default_to_test_accession()
        testing_index = 0
        for client in to_test:
            response: Response = client.patch(f"{self.path}")
            self.assert_http_not_3xx_code(response)
            self.assert_http_denied_access_with_addition(response, f"Case: {testing_index} index fail test")
            testing_index += 1

    def test_who_cannot_delete(self):
        to_test = self._get_default_to_test_accession()
        testing_index = 0
        for client in to_test:
            response: Response = client.delete(f"{self.path}")
            self.assert_http_not_3xx_code(response)
            self.assert_http_denied_access_with_addition(response, f"Case: {testing_index} index fail test")
            testing_index += 1

    def test_save_data_on_update(self):
        to_test: dict[str, any] = {
            "username": "test",
            "email": "test@mail.ru"
        }
        self._test_save_data_on_update(to_test)

    def _test_save_data_on_update(self, to_test):
        su_client: APIClient = get_superuser_client()
        for field_name, value in to_test.items():
            user: User = create_unique_user()
            data = {field_name: value}
            response: Response = su_client.patch(f"{self.path}{user.id}/", data=data)
            self.assert_http_200_with_addition(response, f" Case: {field_name}-{value} not updated")
            updated_user: User = User.objects.get(id=user.id)
            self.assertEqual(updated_user.__dict__[field_name], user.__dict__[field_name])

    def test_output_data_on_get_one(self):
        su_client: APIClient = get_superuser_client()
        expected_data = self._get_expected_data_for_output_data_test()

        response: Response = su_client.get(f"{self.path}{expected_data['id']}/")
        self.assert_http_200(response)
        self.assertTrue(hasattr(response, "data"), msg="Response has not data")
        self.assertEqual(expected_data, response.data, msg="Response not expected")

    def test_output_data_on_get_all(self):
        su_client: APIClient = get_superuser_client()
        user1 = self._get_expected_data_for_output_data_test()
        user2 = create_unique_user()
        expected_data = [
            {
                "id": user1["id"],
                "username": user1["username"],
                "email": user1["email"],
            },
            {
                "id": user2.id,
                "username": user2.username,
                "email": user2.email,
            }
        ]

        response: Response = su_client.get(self.path)
        self.assert_http_200(response)
        self.assertTrue(hasattr(response, "data"), msg="Response has not data")
        self.assertTrue(expected_data[0] in response.data,
                        msg="Response not expected. First user isn't in response")
        self.assertTrue(expected_data[1] in response.data,
                        msg="Response not expected. Second user isn't in response")

    @staticmethod
    def _get_expected_data_for_output_data_test() -> dict[str, any]:
        user: User = create_unique_user()
        give_role(user, Role.WRITER)
        post = create_post(owner=user.id)
        post_serialized = PostSerializer(instance=post)
        expected_data = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "posts": [post_serialized.data],
            "roles": [Role.WRITER]
        }
        return expected_data

    @staticmethod
    def _get_default_to_test_accession() -> list[APIClient]:
        anon_user_client = APIClient()
        authenticated_user_client = get_authenticated_client()
        return [anon_user_client, authenticated_user_client]


class RegistrationTestCase(TestCase, HTTPAsserts):
    path: str = "/registration/"

    def test_registration(self):
        data = generate_dict_to_request_to_create_unique_user()
        client = APIClient()
        response: Response = client.post(self.path, data=data)
        self.assert_http_201(response)
        User.objects.get(id=response.data["id"])

    def test_validation_on_registration(self):
        to_test_invalid, to_test_valid = _get_data_for_validation_test_on_create_user()
        self._test_invalid_data_on_registration(to_test_invalid)
        self._test_valid_data_on_registration(to_test_valid)

    def _test_valid_data_on_registration(self, to_test_valid):
        client = APIClient()
        for field_name, value_list in to_test_valid.items():
            for value in value_list:
                data = generate_dict_to_request_to_create_unique_user(**{field_name: value})
                response: Response = client.post(self.path, data=data)
                self.assert_http_201_with_addition(response, f" Case: {field_name}-{value}")

    def _test_invalid_data_on_registration(self, to_test_invalid):
        client = APIClient()
        for field_name, value_list in to_test_invalid.items():
            for value in value_list:
                data = generate_dict_to_request_to_create_unique_user(**{field_name: value})
                response: Response = client.post(self.path, data=data)
                self.assert_http_400_with_addition(response, f" Case: {field_name}-{value}")

    def test_unique_on_registration(self):
        to_test: dict[str, any] = _get_data_for_unique_test_user()
        for field_name, value in to_test.items():
            data = generate_dict_to_request_to_create_unique_user(**{field_name: value})
            client = APIClient()
            response: Response = client.post(self.path, data=data)
            self.assert_http_201_with_addition(response, f" Case: {field_name}-{value}")
            response: Response = client.post(self.path, data=data)
            self.assert_http_400_with_addition(response, f" Case: {field_name}-{value}")

    def test_who_can_registration(self):
        to_test = [APIClient()]
        testing_index = 0
        for client in to_test:
            response: Response = client.post(f"{self.path}")
            self.assert_http_not_3xx_code(response)
            self.assert_http_provided_access_with_addition(response, f"Case: {testing_index} index fail test")
            testing_index += 1

    def test_who_cannot_registration(self):
        client = get_authenticated_client()
        to_test = [client]
        testing_index = 0
        for client in to_test:
            response: Response = client.post(f"{self.path}")
            self.assert_http_not_3xx_code(response)
            self.assert_http_denied_access_with_addition(response, f"Case: {testing_index} index fail test")
            testing_index += 1


class RoleRequestTestCase(TestCase, HTTPAsserts):
    path: str = "/role-requests/"

    def test_can_get_all(self):
        client = get_superuser_client()
        response: Response = client.get(self.path)
        self.assert_http_200(response)

    def test_get_one(self):
        client = get_superuser_client()
        response = self._create_role_request(client)
        response: Response = client.get(f"{self.path}{response.data['id']}/")
        self.assert_http_200(response)

    def test_post(self):
        client = get_superuser_client()
        self._create_role_request(client)

    def test_patch(self):
        client = get_superuser_client()
        response = self._create_role_request(client)
        response = client.patch(f"{self.path}{response.data['id']}/", data={"message": "Give me"})
        self.assert_http_200(response)

    def test_put(self):
        client = get_superuser_client()
        response = self._create_role_request(client)
        data = {**response.data, "message": "Give me"}
        response = client.put(f"{self.path}{response.data['id']}/", data=data)
        self.assert_http_200(response)

    def test_delete(self):
        client = get_superuser_client()
        response = self._create_role_request(client)
        response = client.delete(f"{self.path}{response.data['id']}/")
        self.assert_http_204(response)

    def test_validation(self):
        to_test_invalid: dict[str, list] = {
            "expected_role": ["invalid", 13]
        }
        to_test_valid: dict[str, list] = {
            "expected_role": [Role.WRITER, Role.ADMIN, Role.SUPERUSER,
                              Role.EDITOR, Role.MODERATOR],
            "message": ["Give me a role!", ""]
        }
        self._test_invalid_data(to_test_invalid)
        self._test_valid_data(to_test_valid)

    def _test_invalid_data(self, to_test_valid):
        su_client = get_superuser_client()
        role_request = self._create_role_request(su_client)
        for field_name, value_list in to_test_valid.items():
            for value in value_list:
                data = {field_name: value}
                response: Response = su_client.patch(f"{self.path}{role_request.data['id']}/",
                                                     data=data)
                self.assert_http_400(response)

    def _test_valid_data(self, to_test_valid):
        su_client = get_superuser_client()
        role_request = self._create_role_request(su_client)
        for field_name, value_list in to_test_valid.items():
            for value in value_list:
                data = {field_name: value}
                response: Response = su_client.patch(f"{self.path}{role_request.data['id']}/",
                                                     data=data)
                self.assert_http_200(response)

    def test_who_can_get_all(self):
        client = get_authenticated_client()
        admin_client = get_admin_client()
        su_client = get_superuser_client()

        to_test = [client, admin_client, su_client]
        testing_index = 0
        for client in to_test:
            response: Response = client.get(self.path)
            self.assert_http_not_3xx_code(response)
            self.assert_http_provided_access_with_addition(response, f"Case: {testing_index} index fail test")
            testing_index += 1

    def test_who_cannot_get_all(self):
        to_test = [APIClient()]
        testing_index = 0
        for client in to_test:
            response: Response = client.get(self.path)
            self.assert_http_not_3xx_code(response)
            self.assert_http_denied_access_with_addition(response, f"Case: {testing_index} index fail test")
            testing_index += 1

    def test_who_can_get_one(self):
        owner_client = get_authenticated_client()
        admin_client = get_admin_client()
        su_client = get_superuser_client()

        to_test = [owner_client, admin_client, su_client]
        testing_index = 0
        for client in to_test:
            response = self._create_role_request(owner_client)
            response: Response = client.get(f"{self.path}{response.data['id']}/")
            self.assert_http_not_3xx_code(response)
            self.assert_http_provided_access_with_addition(response, f"Case: {testing_index} index fail test")
            testing_index += 1

    def test_who_cannot_get_one(self):
        owner_client = get_authenticated_client()
        to_test = [APIClient()]
        testing_index = 0
        for client in to_test:
            response = self._create_role_request(owner_client)
            response: Response = client.get(f"{self.path}{response.data['id']}/")
            self.assert_http_not_3xx_code(response)
            self.assert_http_denied_access_with_addition(response, f"Case: {testing_index} index fail test")
            testing_index += 1

    def test_who_can_post(self):
        client = get_authenticated_client()
        to_test = [client]
        testing_index = 0
        for client in to_test:
            data = {"message": "Hello World", "expected_role": Role.WRITER}
            response: Response = client.post(f"{self.path}", data=data)
            self.assert_http_not_3xx_code(response)
            self.assert_http_provided_access_with_addition(response, f"Case: {testing_index} index fail test")
            testing_index += 1

    def test_who_cannot_post(self):
        to_test = [APIClient()]
        testing_index = 0
        for client in to_test:
            data = {"message": "Hello World", "expected_role": Role.WRITER}
            response: Response = client.post(f"{self.path}", data=data)
            self.assert_http_not_3xx_code(response)
            self.assert_http_denied_access_with_addition(response, f"Case: {testing_index} index fail test")

    def test_who_can_patch(self):
        owner_client = get_authenticated_client()

        to_test = [owner_client]
        testing_index = 0
        for client in to_test:
            response = self._create_role_request(owner_client)
            data = {"message": "Hello World", "expected_role": Role.WRITER}
            response: Response = client.patch(f"{self.path}{response.data['id']}/", data=data)
            self.assert_http_not_3xx_code(response)
            self.assert_http_provided_access_with_addition(response, f"Case: {testing_index} index fail test")

    def test_who_cannot_patch(self):
        auth_client = get_authenticated_client()
        owner_client = get_authenticated_client()
        admin_client = get_admin_client()
        su_client = get_superuser_client()

        to_test = [auth_client, admin_client, su_client]
        testing_index = 0
        for client in to_test:
            response = self._create_role_request(owner_client)
            data = {"message": "Hello World", "expected_role": Role.WRITER}
            response: Response = client.patch(f"{self.path}{response.data['id']}/", data=data)
            self.assert_http_not_3xx_code(response)
            self.assert_http_denied_access_with_addition(response, f"Case: {testing_index} index fail test")
            testing_index += 1

    def test_who_can_delete(self):
        owner_client = get_authenticated_client()

        to_test = [owner_client]
        testing_index = 0
        for client in to_test:
            response = self._create_role_request(owner_client)
            response: Response = client.delete(f"{self.path}{response.data['id']}/")
            self.assert_http_not_3xx_code(response)
            self.assert_http_provided_access_with_addition(response, f"Case: {testing_index} index fail test")
            testing_index += 1

    def test_who_cannot_delete(self):
        owner_client = get_authenticated_client()
        client = get_authenticated_client()
        admin_client = get_admin_client()
        su_client = get_superuser_client()

        to_test = [client, admin_client, su_client]
        testing_index = 0
        for client in to_test:
            response = self._create_role_request(owner_client)
            response: Response = client.delete(f"{self.path}{response.data['id']}/")
            self.assert_http_not_3xx_code(response)
            self.assert_http_denied_access_with_addition(response, f"Case: {testing_index} index fail test")
            testing_index += 1

    def test_save_data_on_update(self):
        user = create_unique_user()
        to_test: dict[str, any] = {
            "user": user.id,
            "date": date(2000, 3, 4),
            "status": RoleRequestStatus.APPROVED
        }
        self._test_save_data_on_update(to_test)

    def _test_save_data_on_update(self, to_test):
        owner_client = get_authenticated_client()
        for field_name, value in to_test.items():
            role_request = self._create_role_request(owner_client)
            data = {field_name: value}
            response: Response = owner_client.patch(f"{self.path}{role_request.data['id']}/", data=data)
            self.assert_http_200_with_addition(response, f" Case: {field_name}-{value} not updated")
            updated_role_request: RoleRequest = RoleRequest.objects.get(id=role_request.data['id'])
            self._compare_field(field_name, role_request, updated_role_request)

    def _compare_field(self, field_name, role_request, updated_role_request):
        try:
            self.assertEqual(updated_role_request.__dict__[field_name], role_request.data[field_name])
        except KeyError:
            try:
                self.assertEqual(updated_role_request.__dict__[field_name + "_id"], role_request.data[field_name])
            except KeyError:
                assert f"Cannot compare field '{field_name}'"

    def test_output_data_on_get_one(self):
        owner_client = get_authenticated_client()
        expected_fields = ('date', 'user', 'status', 'message', 'expected_role', 'id')

        response: Response = self._create_role_request(owner_client)
        self.assert_http_201_with_addition(response, " Cannot create instance")
        response: Response = owner_client.get(f"{self.path}{response.data['id']}/")
        self.assert_http_200(response)
        self.assertTrue(hasattr(response, "data"), msg="Response has not data")
        for field in expected_fields:
            self.assertIn(field, response.data)

    def test_output_data_on_get_all(self):
        expected_fields = ('date', 'user', 'status', 'message', 'expected_role', 'id')
        owner_client = get_authenticated_client()

        for i in range(10):
            response: Response = self._create_role_request(owner_client)
            self.assert_http_201_with_addition(response, " Cannot create instance")

        response: Response = owner_client.get(self.path)
        self.assert_http_200(response)
        self.assertTrue(hasattr(response, "data"), msg="Response has not data")
        for instance in response.data:
            for field in expected_fields:
                self.assertIn(field, instance)

    def test_output_data_on_get_all_by_just_authenticated_client(self):
        owner_client = get_authenticated_client()
        client = get_authenticated_client()

        for i in range(10):
            response: Response = self._create_role_request(owner_client)
            self.assert_http_201_with_addition(response, " Cannot create instance")

        response: Response = client.get(self.path)
        self.assert_http_200(response)
        self.assertTrue(hasattr(response, "data"), msg="Response has not data")
        self.assertEqual(0, len(response.data))

    def _create_role_request(self, client):
        data = {"message": "Give me role", "expected_role": Role.WRITER}
        response: Response = client.post(self.path, data=data)
        self.assert_http_201(response)
        return response

