from Posts import serializers, models
from common.views import ModelViewSetWithCustomMixin


class PostViewSet(ModelViewSetWithCustomMixin):
    queryset = models.Post.objects.all()
    serializer_class = serializers.PostSerializer


class BodyViewSet(ModelViewSetWithCustomMixin):
    queryset = models.Body.objects.all()
    serializer_class = serializers.BodySerializer
