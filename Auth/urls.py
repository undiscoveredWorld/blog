from django.urls import path

from . import views

app_name = "Auth"

urlpatterns = [
    path("register/", views.SignUpView.as_view(), name="register"),
    path("login/", views.SignInView.as_view(), name="login"),
    path("logout/", views.SignOutView.as_view(), name="logout"),
    path("profile/<int:id>", views.ProfileView.as_view(), name="profile")
]
