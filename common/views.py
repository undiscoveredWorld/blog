from rest_framework.response import Response
from rest_framework.mixins import CreateModelMixin
from rest_framework.viewsets import ModelViewSet


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
