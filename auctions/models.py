from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    pass

class Auction(models.Model):
    title = models.CharField(max_length=64)
    description = models.CharField(max_length=250)
    price = models.IntegerField()
    url = models.URLField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name="creator")

class WatchItem(models.Model):
    auction = models.ForeignKey(Auction, null=True, on_delete=models.CASCADE, related_name="watchitem")
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name="visitor")

class Bid(models.Model):
    auction = models.ForeignKey(Auction, null=True, on_delete=models.CASCADE, related_name="bid_item")
    bid = models.IntegerField()
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name="bidder")

class Comment():
    pass