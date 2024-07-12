from django.db import models


class Role(models.TextChoices):
    WRITER = 'writer', 'Writer'
    EDITOR = 'editor', 'Editor'
    MODERATOR = 'moderator', 'Moderator'
    ADMIN = 'admin', 'Admin'
    SUPERUSER = 'superuser', 'Superuser'
