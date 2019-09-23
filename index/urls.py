from django.urls import path
from . import views

urlpatterns = [
    path("", views.index_view, name="index"),
    path("profile/", views.profile_view, name="profile"),
    path("top-picks/", views.top_picks, name="topPicks"),
    path("review/", views.review_handler, name="review"),
    path("top/", views.getTopPlaces, name="top"),
    path("more/", views.morePlaces, name="places"),
    path("places/", views.getPlaces, name="more"),
    path("search/", views.searchView, name="search"),
    path("business/<str:business_id>", views.business_view, name="business"),
]
