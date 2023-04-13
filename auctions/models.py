from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    pass

class CategoryItem(models.Model):
    field = models.CharField(max_length=125)

    def __str__(self):
        return f"{self.field}"

class Auction(models.Model):
    title = models.CharField(max_length=64)
    description = models.CharField(max_length=250)
    price = models.IntegerField()
    url = models.URLField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name="creator")
    active = models.BooleanField(default=True)
    category = models.ForeignKey(CategoryItem, on_delete=models.CASCADE, null=True, related_name="categories")

    def __str__(self):
        return f"{self.title}"

class WatchItem(models.Model):
    auction = models.ForeignKey(Auction, null=True, on_delete=models.CASCADE, related_name="watchitem")
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name="visitor")

class Bid(models.Model):
    auction = models.ForeignKey(Auction, null=True, on_delete=models.CASCADE, related_name="bid_item")
    bid = models.IntegerField()
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name="bidder")

class Comment(models.Model):
    auction = models.ForeignKey(Auction, null=True, on_delete=models.CASCADE, related_name="commented_bid")
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name="commentator")
    comment = models.TextField(max_length=250)

    def __str__(self):
        return f"{self.auction} by {self.user}"