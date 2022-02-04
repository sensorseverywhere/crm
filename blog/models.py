from django.contrib.auth import get_user_model
from django.db import models


class Blog(models.Model):
    title = models.CharField(max_length=255)
    post = models.TextField()

    def __str__(self):
        return self.title
