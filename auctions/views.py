from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import *
from django import forms

# Create a form for new auction listing
class ListingForm(forms.Form):
    title = forms.CharField(max_length=64)
    description = forms.CharField(max_length=250)
    price = forms.IntegerField()
    url = forms.URLField()
    category = forms.ModelChoiceField(queryset=CategoryItem.objects.all(), empty_label=None)

class BidForm(forms.Form):
    bid = forms.IntegerField()

class CommentForm(forms.Form):
    comment = forms.CharField(widget=forms.Textarea())     

def index(request):
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

def create(request, user_id):
    if request.method == 'POST':

        # Create a form and populate it with the data from the request
        form = ListingForm(request.POST)

        # Check if form data is valid (server-side)
        if form.is_valid():

            # Isolate the title, description, price, etc from the 'cleaned' version of form data
            title = form.cleaned_data["title"]
            description = form.cleaned_data["description"]
            price = form.cleaned_data["price"]
            url = form.cleaned_data["url"]
            user = User.objects.get(pk=user_id)
            category = form.cleaned_data["category"]
            #active = form.cleaned_data["active"]

            # Create a new auction
            new_auction = Auction(title=title, description=description, price=price, url=url, user=user, category=category)
            new_auction.save()

        else:
            # If the form is invalid, re-render the page with existing information.
            return render(request, "auctions/create.html", {
                "form": ListingForm()
            })

    return render(request, "auctions/create.html", {
        "form": ListingForm()
    })

def listing(request, auction_id):

    auction = Auction.objects.get(pk=auction_id)
    comments = Comment.objects.filter(auction=auction)

    # Check if the auction is active 
    if auction.active:

        if request.method == "POST":

            # Get the user's id from the submitted form data, then get the user
            user_id = int(request.POST["user_id"])
            user = User.objects.get(pk=user_id)

            # Get the auction 
            auction = Auction.objects.get(pk=auction_id)

            # Check if 'watchlist ' submit  
            if 'watchlist' in request.POST:
                # Add a new item to the watchlist 
                watch_item = WatchItem(auction=auction, user=user)
                watch_item.save()
            
            # Check if 'comment' submit
            elif 'add_comment' in request.POST:

                # Take in the data the user submitted and save it as form
                form = CommentForm(request.POST)

                # Check if form data is valid (server-side)
                if form.is_valid():

                    # Isolate the comment from the 'cleaned' version of form data
                    new_comment = form.cleaned_data["comment"]

                    # Add and save the new comment to the Comment database
                    Comment(auction=auction, user=user, comment=new_comment).save()
                
                else:
                    # If the form is invalid, re-render the page  
                    return render(request, "auctions/auction.html", {
                        "auction": auction,
                        "form": BidForm(),
                        "comments": comments,
                        "form_comment": CommentForm(),
                    })
            
            # Check if 'place_bid' submit
            elif 'place_bid' in request.POST:

                # Take in the data the user submitted and save it as form
                form = BidForm(request.POST)

                # Check if form data is valid (server-side)
                if form.is_valid():

                    # Isolate the bid from the 'cleaned' version of form data
                    bid = form.cleaned_data["bid"]

                    # Check if the bid is at least as large as the starting price
                    if bid >= auction.price: 

                        # Check if any bid of an auction has been placed 
                        if Bid.objects.filter(auction=auction_id).exists():
                            
                            bids = Bid.objects.filter(auction=auction_id)
                            count = bids.count() # the number of bids

                            # Check if the bid is greater than the last bid
                            if bid > bids[count-1].bid:
                                # Save the bid 
                                Bid(auction=auction, user=user, bid=bid).save()
                                count +=1

                                return render(request, "auctions/auction.html", {
                                    "auction": auction,
                                    "form": BidForm(), 
                                    "count": count,
                                    "comments": comments,
                                    "form_comment": CommentForm(),
                                })
                                                
                            else:
                                # If the bid is less than the last bid, re-render the page
                                return render(request, "auctions/auction.html", {
                                    "auction": auction,
                                    "form": BidForm(), 
                                    "message": "Error, the bid is not sufficient.",
                                    "comments": comments,
                                    "form_comment": CommentForm(),
                                })
                        else:
                            # If any bid has not been placed, create and save the new bid
                            new_bid = Bid(auction=auction, user=user, bid=bid)
                            new_bid.save()
                            count = 1
                            return render(request, "auctions/auction.html", {
                                    "auction": auction,
                                    "form": BidForm(), 
                                    "count": count,
                                    "comments": comments,
                                    "form_comment": CommentForm(),
                            })
                                        
                    else:
                        # Case when the bid is less than the starting price 
                        return render(request, "auctions/auction.html", {
                            "auction": auction,
                            "form": BidForm(),
                            "message": "Error, the bid must be at least as large as the starting price and greater than the last bid.",
                            "comments": comments,
                            "form_comment": CommentForm(),
                        })
                    
                else:
                    # If the form is invalid, re-render the page  
                    return render(request, "auctions/auction.html", {
                        "auction": auction,
                        "form": form,
                        "comments": comments,
                        "form_comment": CommentForm(),
                    })
            
            # Check if 'close' submit
            elif 'close' in request.POST:
                Auction.objects.filter(pk=auction_id).update(active=False)
                return render(request, "auctions/close_page.html", {
                    "message": "This auction is no longer active.",
                })

        return render(request, "auctions/auction.html", {
            "auction": auction,
            "form": BidForm(),
            "comments": comments,
            "form_comment": CommentForm(),
        })
        
    # If the auction is not active, then show the closing page
    else:

        # Collect the number of bids 
        bids = Bid.objects.filter(auction=auction)

        # Check if bid(s) exist
        if bids.count() != 0:
            max_entry = bids.latest('bid') # finds the latest (max. value) entry.

            # Check if the visitor is the one who has the highest bid
            if request.user == max_entry.user:

                # Show the closing page which says that the visitor has won the auction listing
                return render(request, "auctions/close_page.html", {
                    "message": "This auction is no longer active.",
                    "winner": max_entry.user,
                })
            else:

                # If the visitor is not the one who has the highest bid, then show the closing page with the given message
                return render(request, "auctions/close_page.html", {
                    "message": "This auction is no longer active.",
                })
        else:
            
            # If no bid, show the closing page with given message
            return render(request, "auctions/close_page.html", {
                "message": "This auction is no longer active.",
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

def categories(request):
    categories = CategoryItem.objects.all()
    return render(request, "auctions/categories.html", {
        "categories": categories, 
    })

def category(request, field_id):
    auctions = Auction.objects.filter(category=field_id)
    return render(request, "auctions/category.html", {
        "auctions": auctions, 
    })
