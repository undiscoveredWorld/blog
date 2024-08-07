from rest_framework.authtoken.admin import User
from rest_framework.response import Response
from rest_framework.mixins import CreateModelMixin
from rest_framework.viewsets import ModelViewSet

from Auth.enums import Role
from Auth.models import UserWithRoles


def return_id_only(response: Response) -> Response:
    response.data = {"id": response.data["id"]}
    return response


class ReturnIdOnlyInCreateMixin(CreateModelMixin):
    def create(self, request, *args, **kwargs):
        create_result = super().create(request, *args, **kwargs)
        return_id_only(create_result)
        return create_result


class ModelViewSetWithCustomMixin(ModelViewSet, ReturnIdOnlyInCreateMixin):
    ...


def get_dict_from_request(request):
    data: dict = request.data
    result = {}
    for key, value in data.items():
        result[key] = value
    return {**data, **result}


def is_superuser(user: User) -> bool:
    try:
        user_roles = UserWithRoles.objects.get(user=user)
    except UserWithRoles.DoesNotExist:
        return False
    return Role.SUPERUSER in user_roles.roles and user.is_superuser


def return_modified_response(response: Response, **kwargs) -> Response:
    data = {
        "data": response.data,
        "status": response.status_code,
        "headers": response.headers,
        "content_type": response.content_type,
        "template_name": response.template_name,
        "exception": response.exception,
        **kwargs
    }
    return Response(**data)