from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

app_name = "Posts"

router = DefaultRouter()
router.register(r'posts', views.PostViewSet, basename='post')
router.register(r'bodies', views.BodyViewSet, basename='body')

urlpatterns = [
    path("", include(router.urls)),
]
