from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Listing(models.Model):
    seller = models.CharField(max_length=60)
    title = models.CharField(max_length=60)
    description = models.TextField(max_length=400)
    start_bid = models.IntegerField()
    category = models.CharField(max_length=60)
    image_link = models.CharField(
        max_length=200, default=None, blank=True, null=True)
    creation_date = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title

class Bid(models.Model):
    listing_id = models.IntegerField()
    user_id = models.IntegerField()
    bid = models.IntegerField()

class Comment(models.Model):
    username = models.CharField(max_length=60)
    listing_id = models.IntegerField()
    user_id = models.IntegerField()
    comment = models.TextField(max_length=400)
    creation_date = models.DateTimeField(auto_now_add=True)

class WatchList(models.Model):
    listing_id = models.IntegerField()
    user_id = models.IntegerField()
    watching = models.BooleanField(default=False)

class Winner(models.Model):
    listing_id = models.IntegerField()
    user_id = models.IntegerField()
    winning_bid = models.IntegerField()
