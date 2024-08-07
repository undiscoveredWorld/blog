from django.contrib.auth.models import User
from rest_framework import status, viewsets
from rest_framework.viewsets import GenericViewSet
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request

from Posts.models import Post
from Posts.serializers import PostSerializer
from common.views import (
    ModelViewSetWithCustomMixin,
    ReturnIdOnlyInCreateMixin,
    get_dict_from_request,
    is_superuser, return_modified_response,
)
from .models import (
    UserWithRoles,
    UserWithRolesSerializer,
    UserSerializer,
    UserUpdateSerializer,
    RoleRequest,
    RoleRequestCreateSerializer,
    RoleRequestGetSerializer,
)
from .permissions import (
    IsNotAuthenticated,
    IsSuperUserOrReadOnly,
    IsOwnerOfRoleRequest
)


class UserViewSet(ModelViewSetWithCustomMixin):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsSuperUserOrReadOnly]

    def create(self, request: Request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        user_id = response.data.get("id")
        self._create_user_with_roles_by_user_id(user_id)
        return response

    @staticmethod
    def _create_user_with_roles_by_user_id(user_id: int) -> None:
        user = User.objects.get(id=user_id)
        data = dict(user=user.id)
        serializer = UserWithRolesSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

    def retrieve(self, request: Request, *args, **kwargs):
        response = super().retrieve(request, *args, **kwargs)

        data = self._serialize_and_get_extra_info_about_user(response)
        data = {**response.data, **data}
        del data["password"]
        return Response(data)

    def list(self, request, *args, **kwargs):
        response: Response = super().list(request, *args, **kwargs)
        data = response.data
        self._delete_password_from_list(response)
        return return_modified_response(response, data=data)

    @staticmethod
    def _delete_password_from_list(response):
        data = response.data
        for instance in data:
            del instance["password"]
        return data

    @staticmethod
    def _serialize_and_get_extra_info_about_user(response: Response) -> dict[str, any]:
        user_id = response.data.get("id")
        user_roles = UserWithRoles.objects.get(user_id=user_id)
        posts = Post.objects.filter(owner_id=user_id).all()
        posts_serializer = PostSerializer(posts, many=True)
        data = {
            "roles": user_roles.roles,
            "posts": posts_serializer.data,
            **response.data
        }
        return data

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = UserUpdateSerializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)


class RegistrationViewSet(GenericViewSet, ReturnIdOnlyInCreateMixin):
    serializer_class = UserSerializer
    http_method_names = ["post"]
    queryset = User.objects.all()
    permission_classes = [IsNotAuthenticated]


class RoleRequestCRUDViewSet(viewsets.ModelViewSet):
    serializer_class = RoleRequestCreateSerializer
    queryset = RoleRequest.objects.all()
    permission_classes = [IsAuthenticated, IsOwnerOfRoleRequest]

    def create(self, request: Request, *args, **kwargs):
        if "user" in request.data.keys():
            return Response(status=status.HTTP_400_BAD_REQUEST)

        role_request = self._create_user_from_request(request)
        headers = self.get_success_headers(role_request.data)
        return Response(role_request.data, status=status.HTTP_201_CREATED, headers=headers)

    def _create_user_from_request(self, request):
        user = request.user
        data = {**get_dict_from_request(request), "user": user.id}
        serializer = self._serialize_and_create_user(data)
        return serializer

    def _serialize_and_create_user(self, data):
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return serializer

    def update(self, request: Request, *args, **kwargs):
        self.get_object()
        user = request.user
        data = {**get_dict_from_request(request), "user": user.id}
        serializer = self._serialize_and_update(data, kwargs)
        return Response(serializer.data)

    def _serialize_and_update(self, data, kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}
        return serializer

    def list(self, request: Request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = RoleRequestGetSerializer(queryset, many=True)
        response = Response(serializer.data)
        return self._cut_response_by_owner_if_need(request, response)

    def _cut_response_by_owner_if_need(self, request, response):
        user = request.user
        if is_superuser(user):
            return response
        user_instances = self._filter_response_by_user(response, user)
        return self._return_modified_response(response, data=user_instances)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = RoleRequestGetSerializer(instance=instance)
        return Response(serializer.data)

    @staticmethod
    def _filter_response_by_user(response, user):
        user_instances = []
        for instance in response.data:
            if instance["user"] == user.id:
                user_instances.append(instance)
        return user_instances

    @staticmethod
    def _return_modified_response(response, **kwargs) -> Response:
        default_kwargs = dict(
            data=response.data,
            headers=response.headers,
            exception=response.exception,
            content_type=response.content_type,
            template_name=response.template_name,
            status=status.HTTP_200_OK
        )
        finally_kwargs = {**default_kwargs, **kwargs}
        return Response(**finally_kwargs)
