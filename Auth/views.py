from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet
from rest_framework.response import Response

from Posts.models import Post
from Posts.serializers import PostSerializer
from common.views import (
    ModelViewSetWithCustomMixin,
    ReturnIdOnlyInCreateMixin,
)
from .models import UserWithRoles, UserSerializer
from .enums import Role
from .permissions import IsSuperUserOrReadOnly


class UserViewSet(ModelViewSetWithCustomMixin):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsSuperUserOrReadOnly]

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        user_id = response.data.get("id")
        user = User.objects.get(id=user_id)
        UserWithRoles.objects.create(user=user, roles=[])
        return response

    def retrieve(self, request, *args, **kwargs):
        response = super().retrieve(request, *args, **kwargs)

        user_id = response.data.get("id")
        user_roles = UserWithRoles.objects.get(user_id=user_id)
        posts = Post.objects.filter(owner_id=user_id).all()
        posts_serializer = PostSerializer(posts, many=True)

        data = {
            "roles": user_roles.roles,
            "posts": posts_serializer.data,
            **response.data
        }
        return Response(data)


class RegistrationViewSet(GenericViewSet, ReturnIdOnlyInCreateMixin):
    serializer_class = UserSerializer
    http_method_names = ["post"]
    queryset = User.objects.all()


class GiveRoleView(APIView):
    def post(self, request, user_id):
        user = User.objects.get(id=user_id)
        user_with_role = UserWithRoles.objects.get(user=user)
        return self._try_append_role(request, user_with_role)

    @staticmethod
    def _try_append_role(request, user_with_role):
        try:
            role = request.data["role"]
            role = Role(role)
            if role not in user_with_role.roles:
                user_with_role.roles.append(role)
                user_with_role.save()
            return Response(status=status.HTTP_200_OK, data=user_with_role.roles)
        except KeyError:
            return Response(status=status.HTTP_400_BAD_REQUEST,
                            data={"role": "Error: Got empty role"})
        except ValueError:
            return Response(status=status.HTTP_400_BAD_REQUEST,
                            data={"role": "Error: Got invalid role"})


class RevokeRoleView(APIView):
    def post(self, request, user_id):
        user = User.objects.get(id=user_id)
        user_with_role = UserWithRoles.objects.get(user=user)
        return self._try_revoke_role(request, user_with_role)

    @staticmethod
    def _try_revoke_role(request, user_with_role):
        try:
            role = request.data["role"]
            role = Role(role)
            if role in user_with_role.roles:
                user_with_role.roles.remove(role)
                user_with_role.save()
            return Response(status=status.HTTP_200_OK, data=user_with_role.roles)
        except KeyError:
            return Response(status=status.HTTP_400_BAD_REQUEST,
                            data={"role": "Error: Got empty role"})
        except ValueError:
            return Response(status=status.HTTP_400_BAD_REQUEST,
                            data={"role": "Error: Got invalid role"})
