from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.urls import reverse
import pandas as pd
from sodapy import Socrata
import requests, random
from django.core.files.images import ImageFile
from .models import UserProfile, Reviews


client = Socrata("data.sfgov.org", None)
# Cover images list to get random from
coverNum = ['/static/cover1.jpg', '/static/cover2.jpg', '/static/cover3.jpg', '/static/cover4.jpg',
'/static/cover5.jpg', '/static/cover6.jpg', '/static/cover7.jpg', '/static/cover8.jpg',]
# Getting background images from pixabay
key = "13232157-fa70535c272469a569b90e6dd"
photo_request = requests.get("https://pixabay.com/api/", params={"key": key, 
                "q": "restaurant+food", "image_type": "photo", "category": "food"})
response = photo_request.json()
photos = []
# Photos["hits"]["count"]
for hit in response["hits"]:
    photos.append(hit["webformatURL"])
headline =["Get reviews on restaurants near you", "We give recommendations too", 
"How did the food taste?", "Hey, we collect restaurant reviews for you", "Join many others to evalu8 restaurants",
"Lots of restaurant reviews for you", "Before you eat, evalu8!!"]
def index_view(request):
    results = client.get("pyih-qa8i", limit=1000)
    context ={
        "user": request.user,
        "results": results,
        "photos": photos,
        "coverPhotos": coverNum,
        "headline": headline
    }
    return render(request, "index.html", context)

def business_view(request, business_id):
    bus_id= int(business_id)
    business_request = requests.get("https://data.sfgov.org/resource/pyih-qa8i.json",
                                    params={"business_id": bus_id})
    business = business_request.json()
    # Result to display for more restaurants
    results = client.get("pyih-qa8i", limit=10)
    username = request.user.username
    profile = UserProfile.objects.get(username=username)
    context ={
        "user": request.user,
        "business_id": bus_id,
        "business": business[0],
        "results": results,
        "photos": photos,
        "profile": profile,
        "reviews": Reviews.objects.filter(business_id = business_id),
    }
    return render(request, "business.html", context)

def profile_view(request):
    username = request.user.username
    if request.method == 'POST':
        if request.FILES['image'] is not None:
            username = request.user.username
            wrapped_file = ImageFile(request.FILES['image'])
            filename = wrapped_file.name
        
            profile = UserProfile()
            profile.image = request.FILES['image']
            profile.username = username
            try:
                profile.save()
                context ={
                    "user": request.user,
                    "successProfile": "Profile Image Successfully Uploaded"
                }
                return render(request, "profile.html", context)
            except OSError:
                context ={
                    "user": request.user,
                    "message": "Profile Save Failed"
                }
                return render(request, "profile.html", context)
    profile = UserProfile.objects.get(username=username)    
    context ={
        "user": request.user,
        "profile": profile,
    }
    return render(request, "profile.html", context)

def review_handler(request):
    if request.method =="POST":
        username = request.user.username
        business_id = request.POST["business_id"]
        text = request.POST["text"]
        timestamp = request.POST["timestamp"]
        image = request.POST["image"]

        review = Reviews ()
        review.business_id =business_id
        review.username = username
        review.image_url = image 
        review.review_text = text
        review.timestamp = timestamp
        review.save()

        bus_id= int(business_id)
        business_request = requests.get("https://data.sfgov.org/resource/pyih-qa8i.json",
                                    params={"business_id": bus_id})
        business = business_request.json()
        # Result to display for more restaurants
        results = client.get("pyih-qa8i", limit=10)
        profile = UserProfile.objects.get(username=username)
        context ={
            "user": request.user,
            "reviews": Reviews.objects.filter(business_id = business_id),
            "successMessage": "Review successfully submitted",
            "business_id": bus_id,
            "business": business[0],
            "results": results,
            "photos": photos,
            "profile": profile,
        }
        # Return page with new review in it
        return render(request, "business.html", context)

    return None