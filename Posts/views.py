from rest_framework import viewsets

from Posts import serializers, models


class PostViewSet(viewsets.ModelViewSet):
    queryset = models.Post.objects.all()
    serializer_class = serializers.PostSerializer


class BodyViewSet(viewsets.ModelViewSet):
    queryset = models.Body.objects.all()
    serializer_class = serializers.BodySerializer
