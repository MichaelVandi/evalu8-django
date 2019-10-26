from django.urls import path, re_path
from django.urls import include
from django.contrib.auth.views import (PasswordResetView, PasswordResetDoneView, 
    PasswordResetConfirmView, PasswordResetCompleteView, TemplateView
)


from . import views

urlpatterns = [
    path("", views.login_view, name="default"),
    path("login/", views.login_view, name="login"),
    path("signup/", views.signup, name="signup"),
    path("logout/", views.logout_view, name="logout"),
    path('reset-password/', PasswordResetView.as_view(), name= 'reset_password'),
    path('reset-password/done', PasswordResetDoneView.as_view(), name="password_reset_done"),
    re_path(r'^reset-password/confirm/(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)/$', PasswordResetConfirmView.as_view(), name="password_reset_confirm"),
    path('reset-password/complete', PasswordResetCompleteView.as_view(), name="password_reset_complete")
]
