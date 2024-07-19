from django.views.generic.detail import DetailView
from django.contrib.auth.models import User
from rest_framework import viewsets

from .serializers import UserSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class ProfileView(DetailView):
    template_name = 'auth/profile.html'
    model = User
    context_object_name = 'profile'
    pk_url_kwarg = 'id'
