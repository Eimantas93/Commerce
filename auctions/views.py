from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.db.models import Max, Count
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, reverse
from django.urls import reverse
from . models import Listing, WatchList, Bid, Winner, Comment
import django_filters

from .models import User


def index(request):
    listings = Listing.objects.all()
    return render(request, "auctions/index.html", {"listings":listings})


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

def create_listing_view(request):
    if request.method == "POST":
        item = Listing()
        item.seller = request.user.username
        item.title = request.POST.get('title')
        item.description = request.POST.get('description')
        item.start_bid = request.POST.get('starting_bid')
        item.category = request.POST.get('category')
        item.image_link = request.POST.get('image_link')
        item.duration_days = request.POST.get('duration_days')
        item.save()
        return render(request, 'auctions/index.html')
    else:
        return render(request, "auctions/create_listing.html")

def listing_view(request, id):

    added_to_watchlist = False
    logged_in = False
    is_creator = False

    listing = Listing.objects.get(id=id)
    watched_item = WatchList.objects.filter(listing_id=id, user_id=request.user.id)
    all_listing_bids = Bid.objects.filter(listing_id=id)
    users_comments = Comment.objects.filter(listing_id=id)

    if all_listing_bids:
        max_bid = all_listing_bids.aggregate(Max('bid'))
        highest_bid = max_bid["bid__max"]
    else:
        highest_bid = None

    # GET method
    if request.method == 'GET':

        user_id = request.user.id

        if Winner.objects.filter(listing_id=id, user_id=request.user.id):
            max_bid_row = Bid.objects.filter(listing_id=id).order_by('-bid').first()
            winner_id = max_bid_row.user_id
        else:
            winner_id = 0

        if listing.seller == request.user.username:
            is_creator = True
        if request.user.is_authenticated:
            logged_in = True
        if watched_item:
            added_to_watchlist = True
        return render(request, "auctions/listing_page.html", {
            "listing":listing, 
            "added_to_watchlist":added_to_watchlist, 
            "logged_in":logged_in, 
            "highest_bid":highest_bid,
            "is_creator":is_creator,
            "winner_id":winner_id,
            "user_id":user_id,
            "users_comments":users_comments
            })
    
    # POST method
    else:
        bids = Bid()
        bid = int(request.POST['bid'])

        if bid >= listing.start_bid:
            if highest_bid is not None:
                if bid > highest_bid:
                    pass
                else:
                    return HttpResponse("Bid is too low")
            bids.listing_id = id
            bids.user_id = request.user.id
            bids.bid = bid
            bids.save()
        else:
            return HttpResponse("Bid is too low")

        return HttpResponseRedirect(reverse("listing", args=(id,)))


def watch_view(request, listing_id):
    watched_item = WatchList.objects.filter(listing_id=listing_id, user_id=request.user.id)
    if watched_item:
        watched_item.delete()
        return HttpResponseRedirect(reverse("listing", args=(listing_id,)))

    watching_item = WatchList()

    watching_item.user_id = request.user.id
    watching_item.listing_id = listing_id
    watching_item.watching = True
    watching_item.save()
    return HttpResponseRedirect(reverse("listing", args=(listing_id,)))

def close_listing_view(request, listing_id):
    current_listing = Listing.objects.get(id=listing_id)
    current_listing.is_active = False

    current_listing.save()


    max_bid_row = Bid.objects.filter(listing_id=listing_id).order_by('-bid').first()

    new_winner = Winner()
    new_winner.listing_id = listing_id
    new_winner.user_id = max_bid_row.user_id
    new_winner.winning_bid = max_bid_row.bid

    new_winner.save()

    return HttpResponseRedirect(reverse("listing", args=(listing_id,)))

def comment_view(request, listing_id):
    user_comment = request.POST['comment']

    new_comment = Comment()
    new_comment.username = request.user.username
    new_comment.user_id = request.user.id
    new_comment.listing_id = listing_id
    new_comment.comment = user_comment
    new_comment.save()

    return HttpResponseRedirect(reverse("listing", args=(listing_id,)))

def my_watch_list_view(request):
    user_id = request.user.id

    watchlist_rows = WatchList.objects.filter(user_id=user_id, watching=True)

    listings = Listing.objects.all()

    return render(request, "auctions/my_watch_list.html", {"listings":listings, "watchlist_rows":watchlist_rows})

def categories(request):

    grouped_listings = Listing.objects.values('category').annotate(dcount=Count('category'))

    if request.method == "GET":
        listings = Listing.objects.all()

        return render(request, "auctions/categories.html", {"grouped_listings":grouped_listings, "listings":listings})
    else:
        category = request.POST['category']
        listings = Listing.objects.filter(category=category)

        return render(request, "auctions/categories.html", {"grouped_listings":grouped_listings, "listings":listings})
