from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

app_name = "Auth"

router = DefaultRouter()
router.register(r"users", views.UserViewSet, basename="user")

urlpatterns = [
    path("", include(router.urls)),
    path("profile/<int:id>", views.ProfileView.as_view(), name="profile"),
    path("give_role/<int:user_id>", views.GiveRoleView.as_view(), name="give_role"),
    path("revoke_role/<int:user_id>", views.RevokeRoleView.as_view(), name="give_role")
]
