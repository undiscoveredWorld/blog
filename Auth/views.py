from django.views.generic.detail import DetailView
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from common.views import ModelViewSetWithCustomMixin
from .models import UserWithRoles
from .serializers import UserSerializer
from .enums import Role


class UserViewSet(ModelViewSetWithCustomMixin):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        user_id = response.data.get("id")
        user = User.objects.get(id=user_id)
        UserWithRoles.objects.create(user=user, roles=[])
        return response


class ProfileView(DetailView):
    template_name = 'auth/profile.html'
    model = User
    context_object_name = 'profile'
    pk_url_kwarg = 'id'


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
