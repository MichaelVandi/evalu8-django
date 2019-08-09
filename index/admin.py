from django.contrib import admin
from .models import UserProfile, Reviews

# Register your models here.

admin.site.register(UserProfile)
admin.site.register(Reviews)