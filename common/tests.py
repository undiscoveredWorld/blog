from abc import ABC, abstractmethod

from rest_framework import status
from rest_framework.response import Response


class HTTPAsserts(ABC):
    def assert_http_200(self, response: Response):
        self.assertEqual(response.status_code, status.HTTP_200_OK,
                         msg=self._get_assert_http_200_message(response))

    def assert_http_201(self, response: Response):
        self.assertEqual(response.status_code, status.HTTP_201_CREATED,
                         msg=self._get_assert_http_201_message(response))

    def assert_http_204(self, response: Response):
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT,
                         msg=self._get_assert_http_204_message(response))

    def assert_http_not_3xx_code(self, response: Response):
        self.assertFalse(300 <= response.status_code < 400,
                         self._get_assert_http_not_3xx_message(response))

    def assert_http_400(self, response: Response):
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST,
                         msg=self._get_assert_http_400_message(response))

    def assert_http_200_with_addition(self, response: Response, addition: str):
        self.assertEqual(response.status_code, status.HTTP_200_OK,
                         msg=self._get_assert_http_200_message(response) + addition)

    def assert_http_201_with_addition(self, response: Response, addition: str):
        self.assertEqual(response.status_code, status.HTTP_201_CREATED,
                         msg=self._get_assert_http_201_message(response) + addition)

    def assert_http_400_with_addition(self, response: Response, addition: str):
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST,
                         msg=self._get_assert_http_400_message(response) + addition)

    def assert_http_denied_access_with_addition(self, response: Response, addition: str):
        self.assertTrue(response.status_code in [401, 403],
                        msg=self._get_assert_http_denied_access_message(response) + addition)

    def assert_http_provided_access_with_addition(self, response: Response, addition: str):
        self.assertTrue(response.status_code not in [401, 403],
                        msg=self._get_assert_http_provided_access_message(response) + addition)

    def _get_assert_http_200_message(self, response: Response):
        return self._invalid_response_message(response)

    def _get_assert_http_201_message(self, response: Response):
        return self._invalid_response_message(response)

    def _get_assert_http_204_message(self, response: Response):
        return self._invalid_response_message(response)

    @staticmethod
    def _invalid_response_message(response: Response):
        if hasattr(response, "data"):
            return f"Invalid response. Detail: {response.data}"
        else:
            return "Invalid response"

    @staticmethod
    def _get_assert_http_not_3xx_message(response: Response):
        if hasattr(response, "data"):
            return f"{response.status_code}:{response.data}"
        else:
            return f"3xx code alert"

    @staticmethod
    def _get_assert_http_400_message(response: Response):
        if hasattr(response, "data"):
            return f"Response must be 400. Detail: {response.data}"
        else:
            return "Response must be 400"

    @staticmethod
    def _get_assert_http_denied_access_message(response: Response):
        if hasattr(response, "data"):
            return f"Access not denied. Detail: {response.status_code}-{response.data}"
        else:
            return "Access not denied"

    @staticmethod
    def _get_assert_http_provided_access_message(response: Response):
        if hasattr(response, "data"):
            return f"Access not provided. Detail: {response.status_code}-{response.data}"
        else:
            return "Access not provided"

    @abstractmethod
    def assertTrue(self, expression, msg=None):
        pass

    @abstractmethod
    def assertFalse(self, expression, msg=None):
        pass

    @abstractmethod
    def assertEqual(self, first, second, msg=None):
        pass

    @abstractmethod
    def assertNotEqual(self, first, second, msg=None):
        pass

