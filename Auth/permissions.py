from django.contrib.auth.models import User
from rest_framework import permissions
from rest_framework.request import Request

from Auth.enums import Role
from Auth.models import UserWithRoles, RoleRequest


def _user_have_role(user: User, role: Role) -> bool:
    user_roles = UserWithRoles.objects.filter(user=user)
    if not user_roles.exists():
        return False
    user_roles = user_roles.get()
    return role in user_roles.roles


class IsNotAuthenticated(permissions.BasePermission):
    def has_permission(self, request, view):
        return not request.user.is_authenticated


class IsSuperUserOrReadOnly(permissions.BasePermission):
    def has_permission(self, request: Request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        if not request.user.is_authenticated:
            return False
        return _user_have_role(request.user, Role.SUPERUSER)


class IsOwnerOfRoleRequest(permissions.BasePermission):
    def has_permission(self, request: Request, view):
        if request.method == 'GET':
            return self._handle_get(request, view)
        if request.method in ['PUT', 'PATCH', 'DELETE']:
            role_request = view.get_object()
            if role_request:
                return self._is_owner(request, role_request)
        return True

    def _handle_get(self, request, view):
        try:
            role_request = view.get_object()
            user = request.user
            return (self._is_owner(request, role_request) or
                    _user_have_role(user, Role.ADMIN) or
                    _user_have_role(user, Role.SUPERUSER))
        except AssertionError:
            return True

    @staticmethod
    def _is_owner(request: Request, role_request: RoleRequest) -> bool:
        user = request.user
        if role_request.user.id != user.id:
            return False
        return True
