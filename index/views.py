from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.urls import reverse
import pandas as pd
from sodapy import Socrata
import requests, random, json, time
from django.core.files.images import ImageFile
from django.views.decorators.csrf import csrf_exempt
from .models import UserProfile, Reviews
from django.contrib.auth.models import User


client = Socrata("data.sfgov.org", None)
# Cover images list to get random from
coverNum = ['/static/cover1.jpg', '/static/cover2.jpg', '/static/cover3.jpg', '/static/cover4.jpg',
'/static/cover5.jpg', '/static/cover6.jpg', '/static/cover7.jpg', '/static/cover8.jpg',]
# Getting background images from pixabay
key = "13232157-fa70535c272469a569b90e6dd"
photo_request = requests.get("https://pixabay.com/api/", params={"key": key, 
                "q": "restaurant+food", "image_type": "photo", "category": "food", "page":3, "per_page": 100})
response = photo_request.json()
photos = []
# Photos["hits"]["count"]
for hit in response["hits"]:
    photos.append(hit["webformatURL"])
headline =["Get reviews on restaurants near you", "We give recommendations too", 
"How did the food taste?", "Hey, we collect restaurant reviews for you", "Join many others to evalu8 restaurants",
"Lots of restaurant reviews for you", "Before you eat, evalu8!!"]
def index_view(request):
    results = client.get("pyih-qa8i")
    result_num = len(results)
    context ={
        "user": request.user,
        "results": results,
        "photos": photos,
        "coverPhotos": coverNum,
        "headline": headline,
        "resultNum": result_num
    }
        
    return render(request, "index.html", context)
def top_picks(request):
    results = client.get("pyih-qa8i", where = "inspection_score > 90", limit=10,)
    result_num = len(results)
    context ={
        "user": request.user,
        "results": results,
        "photos": photos,
        "coverPhotos": coverNum,
        "headline": headline,
        "resultNum": result_num,
        "toppicks" : "True"
    }
        
    return render(request, "top_index.html", context)

@csrf_exempt
def searchView(request):
    if request.method == 'POST':
        city = str(request.POST['city'] or "San Francisco")
        name = str(request.POST['name'])
        # Different case variations of name
        capital_name = name.capitalize()
        title_name = name.title()
        upper_case_name = name.upper()
        lower_case_name = name.lower()

        query_string ="business_name like '%" + name + "%' OR business_address like '%" + name + "%'" + "OR " +\
        "business_name like '%" + capital_name + "%' OR business_address like '%" + capital_name + "%'" + "OR " +\
        "business_name like '%" + title_name + "%' OR business_address like '%" + title_name + "%'" + "OR " +\
        "business_name like '%" + upper_case_name + "%' OR business_address like '%" + upper_case_name + "%'" + "OR " +\
        "business_name like '%" + lower_case_name + "%' OR business_address like '%" + lower_case_name + "%'"

        results = client.get("pyih-qa8i", where = query_string, limit=1000)
        context ={
            "user": request.user,
            "results": results,
            "photos": photos,
            "city": city,
            "name": name,
            "coverPhotos": coverNum,
            "headline": headline,
        }
        return render(request, "search.html", context)
    else:
        return("No search request posted")

@csrf_exempt
def getPlaces(request):
    results = client.get("pyih-qa8i", limit=5000)
    # Get start and end point for posts to generate.
    start = int(request.GET['start'] or 0)
    end = int(request.GET['end'] or (start + 9))

    # Generate list of posts.
    data = []
    for i in range(start, end + 1):
        data.append(results[i])

    # Artificially delay speed of response.
    time.sleep(1)

    # Return list of posts.
    return HttpResponse(json.dumps(data))

@csrf_exempt
def getTopPlaces(request):
    results = client.get("pyih-qa8i", where = "inspection_score > 90", limit=5000)
    # Get start and end point for posts to generate.
    start = int(request.GET['start'] or 0)
    end = int(request.GET['end'] or (start + 9))

    # Generate list of posts.
    data = []
    for i in range(start, end + 1):
        data.append(results[i])

    # Artificially delay speed of response.
    time.sleep(1)

    # Return list of posts.
    return HttpResponse(json.dumps(data))

@csrf_exempt
def morePlaces(request):
    # Get start and end point for posts to generate.
    if request.method == 'GET':
        start = int(request.GET['start'] or 20)
        end = int(request.GET['end'] or (start + 9))
        latitude = request.GET['latitude']
        longitude = request.GET['longitude']

        latitude_upper = float(float(latitude) + 0.05)
        latitude_lower = float(float(latitude) - 0.05)
        longitude_upper = float(float(longitude) + 0.05)
        longitude_lower = float(float(longitude) - 0.05)
        query_string = "business_latitude between "+ str(latitude_lower) +" and " + str(latitude_upper) +\
        " AND "+ "business_longitude between "+ str(longitude_lower) + " and " + str(longitude_upper)
        # If the request contains inspection score: Meaning its coming from the 'higher score finder' button, change
        # the query string
        if 'inspection_score' in request.GET:
            query_string = "business_latitude between "+ str(latitude_lower) +" and " + str(latitude_upper) +\
        " AND "+ "business_longitude between "+ str(longitude_lower) + " and " + str(longitude_upper) +\
        " AND "+ "inspection_score > "+ str(request.GET['inspection_score'])

        # Make request to API with query injected
        results = client.get("pyih-qa8i", where = query_string, limit=500)
        # Generate list of posts.
        data = []
        for i in range(start, end + 1):
            data.append(results[i])

        # Artificially delay speed of response.
        time.sleep(1)

        # Return list of posts.
        return HttpResponse(json.dumps(data))

def business_view(request, business_id):
    bus_id= int(business_id)
    business_request = requests.get("https://data.sfgov.org/resource/pyih-qa8i.json",
                                    params={"business_id": bus_id})
    business_raw = business_request.json()
    business = business_raw[0]
    # Result to display for more restaurants
    results = client.get("pyih-qa8i", limit=20)
    username = request.user.username
    location_exists = False
    if request.user.is_authenticated:
        profile = UserProfile.objects.get(username=username)
    else:
        profile =[]
    # if location exists make a soql query to get nearby restaurants
    business_location = business.get("business_location", None)
    if business_location == None:
        # No location exist, get another shot of it from the google places API on client side.
        location_exists = False
    else:
        # Location exists, get latitude and longitude
        latitude_upper = float(float(business["business_latitude"]) + 0.05)
        latitude_lower = float(float(business["business_latitude"]) - 0.05)
        longitude_upper = float(float(business["business_longitude"]) + 0.05)
        longitude_lower = float(float(business["business_longitude"]) - 0.05)
        query_string = "business_latitude between "+ str(latitude_lower) +" and " + str(latitude_upper) +\
        " AND "+ "business_longitude between "+ str(longitude_lower) + " and " + str(longitude_upper)
        # Make request to API with query injected
        results = client.get("pyih-qa8i", where = query_string, limit=20)
        location_exists = True
            
    context ={
        "user": request.user,
        "business_id": bus_id,
        "business": business,
        "results": results,
        "location_exists": location_exists,
        "photos": photos,
        "profile": profile,
        "reviews": Reviews.objects.filter(business_id = business_id),
    }
    return render(request, "business.html", context)
@csrf_exempt
def profile_view(request):
    username = request.user.username
    if request.method == 'POST':
        # If Post request contains 'image' run this
        if 'image' in request.POST:
            if request.FILES['image'] is not None:
                username = request.user.username
                wrapped_file = ImageFile(request.FILES['image'])
                filename = wrapped_file.name
            
                profile = UserProfile()
                profile.image = request.FILES['image']
                profile.username = username
                try:
                    profile.save()
                    new_profile = UserProfile.objects.get(username=username) 
                    context ={
                        "user": request.user,
                        "profile": new_profile,
                        "successProfile": "Profile Image Successfully Uploaded"
                    }
                    return render(request, "profile.html", context)
                except OSError:
                    new_profile = UserProfile.objects.get(username=username)  
                    context ={
                        "user": request.user,
                        "profile": new_profile,
                        "message": "Profile Save Failed"
                    }
                    return render(request, "profile.html", context)
        if 'firstName' in request.POST:
            # Set values
            # Profile Account object contains attributes like image, mobile, city
            profileAccount = UserProfile.objects.get(username = request.user.username)
            # User Account object contains basic user attributes
            userAccount = User.objects.get(username = request.user.username)
            userAccount.first_name = str(request.POST['firstName'])
            userAccount.last_name = str(request.POST['lastName'])
            userAccount.email = str(request.POST['email'])

            profileAccount.city = str(request.POST['city'])
            profileAccount.mobile = str(request.POST['mobileNumber'])
            try:
                profileAccount.save()
                userAccount.save()
                # Return new user and profile accounts
                new_profile = UserProfile.objects.get(username=request.user.username) 
                context ={
                    "user": request.user,
                    "profile": new_profile,
                    "messagePositive": "Profile Successfully Saved"
                }
                return render(request, "profile.html", context)
            except OSError:
                new_profile = UserProfile.objects.get(username=request.user.username) 
                context ={
                    "user": request.user,
                    "profile": new_profile,
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