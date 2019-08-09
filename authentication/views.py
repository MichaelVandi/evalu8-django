from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.models import User
from django.db import IntegrityError
from index.models import UserProfile

coverNum = ['/static/cover1.jpg', '/static/cover2.jpg', '/static/cover3.jpg', '/static/cover4.jpg',
'/static/cover5.jpg', '/static/cover6.jpg', '/static/cover7.jpg', '/static/cover8.jpg',]


def login_view(request):
    context ={
    "coverPhotos": coverNum
    }
    if request.method == 'POST':
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username = username, password = password)
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "login.html", {"message": "Invalid credentials.", "coverPhotos": coverNum})
    return render(request, "login.html", {"message": "", "coverPhotos": coverNum})
    
def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))

def signup(request):
    context ={
    "coverPhotos": coverNum
    }
    if request.method == 'POST':
        username = request.POST["username"]
        password= request.POST["password"]
        confirm= request.POST["confirm"]
        first_name= request.POST["firstname"]
        last_name= request.POST["lastname"]
        email= request.POST["email"]
        # Check if all fields are filled
        if username == '' or password == '' or confirm == '' or first_name == '' \
            or last_name == '' or email == '':
            # One or more fields are empty show message
            return render(request, "signup.html", {"message": "One or more fields empty", "coverPhotos": coverNum})
        if password != confirm:
            # Passwords don match show message
            return render(request, "signup.html", {"message": "Passwords do not match", "coverPhotos": coverNum})
        if len(password) < 6:
            # Passwords Less than 6 chars
            return render(request, "signup.html", {"message": "Password must be six or more characters", "coverPhotos": coverNum})
        # Conditions met, add new user
        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                password = password,
            )
            user.first_name = first_name
            user.last_name = last_name
            user.save()
            # Update user profile too
            profile = UserProfile()
            profile.username =username
            profile.save()
            # New user created redirect user to login page
            return render(request, "login.html", {"new_user_msg": "Welcome "+ first_name + " you can now log in", "coverPhotos": coverNum} )
        except IntegrityError:
            # User already exists
            return render(request, "signup.html", {"message": "User already exist", "coverPhotos": coverNum})

    return render(request, "signup.html", context)


