from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

app_name = "Auth"

router = DefaultRouter()
router.register(r"users", views.UserViewSet, basename="user")

urlpatterns = [
    path("", include(router.urls)),
    path("profile/<int:id>", views.ProfileView.as_view(), name="profile"),
]
