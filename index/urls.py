from django.urls import path

from . import views

urlpatterns = [
    path("", views.index_view, name="index"),
    path("profile/", views.profile_view, name="profile"),
    path("review/", views.review_handler, name="review"),
    path("business/<str:business_id>", views.business_view, name="business")

]
