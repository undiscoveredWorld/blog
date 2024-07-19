from django.db import models
from django.contrib.auth.models import User


class Body(models.Model):
    text = models.TextField()


class Post(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=50)
    body = models.ForeignKey(Body, on_delete=models.CASCADE)
    is_restricted = models.BooleanField(default=False)
    rating = models.FloatField(default=0)
