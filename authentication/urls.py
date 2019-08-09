from django.urls import path
from django.urls import include, path


from . import views

urlpatterns = [
    path("", views.login_view, name="default"),
    path("login", views.login_view, name="login"),
    path("signup", views.signup, name="signup"),
    path("logout", views.logout_view, name="logout"),
]
