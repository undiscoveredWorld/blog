from django.views.generic.detail import DetailView
from django.contrib.auth.models import User

from common.views import ModelViewSetWithCustomMixin
from .serializers import UserSerializer


class UserViewSet(ModelViewSetWithCustomMixin):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class ProfileView(DetailView):
    template_name = 'auth/profile.html'
    model = User
    context_object_name = 'profile'
    pk_url_kwarg = 'id'
