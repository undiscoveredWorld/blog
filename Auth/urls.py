from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

app_name = "Auth"

router = DefaultRouter()
router.register(r"users", views.UserViewSet, basename="user")
router.register(r"registration", views.RegistrationViewSet, basename="registration")
router.register(r"role-requests", views.RoleRequestCRUDViewSet, basename="create-role-request")

urlpatterns = [
    path("", include(router.urls)),
]
