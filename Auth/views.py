from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from django.views.generic.detail import DetailView
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.models import User

from .forms import UserRegisterForm


class SignUpView(SuccessMessageMixin, CreateView):
    template_name = 'auth/register.html'
    success_url = reverse_lazy('login')
    form_class = UserRegisterForm
    success_message = "Your profile was created successfully"


class SignInView(SuccessMessageMixin, LoginView):
    template_name = 'auth/login.html'
    success_url = reverse_lazy('list_posts')
    next_page = "/"


class SignOutView(SuccessMessageMixin, LogoutView):
    template_name = 'auth/logout.html'
    next_page = "/"


class ProfileView(DetailView):
    template_name = 'auth/profile.html'
    model = User
    context_object_name = 'profile'
    pk_url_kwarg = 'id'
