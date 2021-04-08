from django.contrib import admin
from .models import Listing, Bid, Comment, User, WatchList, Winner

# Register your models here.

admin.site.register(User)
admin.site.register(Listing)
admin.site.register(Bid)
admin.site.register(Comment)     
admin.site.register(WatchList)           
admin.site.register(Winner)           
