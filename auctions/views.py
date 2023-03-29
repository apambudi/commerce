from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import *
from django import forms

# Create a form for new auction listing
class NewListingForm(forms.Form):
    title = forms.CharField(max_length=64)
    description = forms.CharField(max_length=250)
    price = forms.IntegerField()
    url = forms.URLField()

def index(request):

    if request.method == 'POST':

        # Finding the user id from the submitted form
        user_id = int(request.POST["user_id"])
        user = User.objects.get(pk=user_id)

        # Finding the auction id from the submitted form 
        auction_id = int(request.POST["auction_id"])
        auction = Auction.objects.get(pk=auction_id)

        # Add a new item to the watchlist 
        watch_item = WatchItem(auction=auction, user=user)
        watch_item.save()

        return HttpResponseRedirect(reverse("index"))
    
    return render(request, "auctions/index.html", {
        "auctions": Auction.objects.all()
    })

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

def create(request):
    if request.method == 'POST':

        # Create a form and populate it with the data from the request
        form = NewListingForm(request.POST)

        # Check if form data is valid (server-side)
        if form.is_valid():

            # Isolate the title, description, price, etc from the 'cleaned' version of form data
            title = form.cleaned_data["title"]
            description = form.cleaned_data["description"]
            price = form.cleaned_data["price"]
            url = form.cleaned_data["url"]
            user = User.objects.get(pk=request.POST["user_id"])

            # Create a new auction
            auction = Auction(title=title, description=description, price=price, url=url, user=user)
            auction.save()

        else:
            # If the form is invalid, re-render the page with existing information.
            return render(request, "auctions/create.html", {
                "form": NewListingForm()
            })

    return render(request, "auctions/create.html", {
        "form": NewListingForm()
    })

def auction(request, auction_id):
    auction = Auction.objects.get(pk=auction_id)

    if request.method == "POST":

        # Get the bid from the submitted form data
        bid = int(request.POST["bid"])

        # Get the user's id from the submitted form data, then get the user
        user_id = int(request.POST["user_id"])
        user = User.objects.get(pk=user_id)

        # Get the auction 
        auction = Auction.objects.get(pk=auction_id)

        if bid >= auction.price: 

            # Check if any bid of an auction has been placed 
            if Bid.objects.filter(auction=auction_id).exists():
    
                last_bid = Bid.objects.filter(auction=auction_id)

                if bid > last_bid[0].bid:
                    Bid.objects.filter(auction=auction_id).update(bid=bid)
                    return HttpResponseRedirect(reverse("index"))
            
                else:
                    return render(request, "auctions/auction.html", {
                    "auction": auction,
                    "message": "Error, the bid is not sufficient."
                })

            # Creating and saving a new bid
            new_bid = Bid(auction=auction, user=user, bid=bid)
            new_bid.save()
            return HttpResponseRedirect(reverse("index"))
        
        else:
            return render(request, "auctions/auction.html", {
                "auction": auction,
                "message": "Error, the bid must be at least as large as the starting bid."
            })

    return render(request, "auctions/auction.html", {
        "auction": auction
    })

def watchlist(request, user_id):
    watch_list = WatchItem.objects.filter(user=user_id)

    if request.method == 'POST':

        # Get an item id from the submitted form
        item_id = int(request.POST["item_id"])

        # Remove the item from the watchlist
        WatchItem.objects.filter(pk=item_id).delete()

        return HttpResponseRedirect(reverse("watchlist", args=(user_id,)))

    return render(request, "auctions/watchlist.html", {
        "list": watch_list
    })

