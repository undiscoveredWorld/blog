from django.contrib import admin

from Posts import models

# Register your models here.
admin.site.register(models.Post)
admin.site.register(models.Body)
