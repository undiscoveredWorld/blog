from rest_framework import permissions
from rest_framework.request import Request

from Auth.enums import Role
from Auth.models import UserWithRoles


class IsSuperUserOrReadOnly(permissions.BasePermission):
    def has_permission(self, request: Request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        if not request.user.is_authenticated:
            return False

        user = request.user
        user_roles = UserWithRoles.objects.filter(user=user)
        if not user_roles.exists():
            return False
        user_roles = user_roles.get()
        return Role.SUPERUSER in user_roles.roles
