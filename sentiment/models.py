from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    email = models.EmailField(max_length=254, unique=True)


class PostLink(models.Model):
    post_url = models.CharField(
        max_length=256, blank=False,
        default="https://www.youtube.com/"
    )
    post_type = models.CharField(
        max_length=256, blank=False, default="youtube"
    )
    last_updated = models.DateField(blank=True, null=True)


class PostComment(models.Model):
    post = models.ForeignKey(PostLink, related_name='link_comment', on_delete=models.CASCADE)
    comments = models.CharField(max_length=256, blank=False, default="Insert youtube comments")
    last_updated = models.DateField(blank=True, null=True)
