from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class UserProfile(models.Model):
    image = models.ImageField(default = 'avatar.png', null= True, blank=True)
    city = models.CharField(max_length = 84, null = True)
    mobile = models.CharField(max_length = 84, null = True)
    username =models.CharField(max_length = 83, null = False, primary_key = True)

    def __str__(self):

        return self.username

class Reviews(models.Model):
    business_id = models.CharField(max_length = 84, null = False)
    username = models.CharField(max_length = 84, null = False)
    image_url = models.CharField(max_length = 100, null = True)
    review_text = models.TextField(null = False)
    timestamp = models.CharField(max_length = 200, null = False)

    def __str__(self):
        
            return f"{self.business_id} {self.username}"