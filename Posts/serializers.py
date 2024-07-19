from rest_framework import serializers

from Posts import models


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = models.Post


class BodySerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = models.Body
