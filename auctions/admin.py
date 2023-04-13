from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(Auction)
admin.site.register(WatchItem)
admin.site.register(Bid)
admin.site.register(Comment)
admin.site.register(CategoryItem)
admin.site.register(User)

