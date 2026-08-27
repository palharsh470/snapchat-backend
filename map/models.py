from django.db import models
from core.models import Profile

class Location(models.Model):
    profile = models.OneToOneField(to=Profile, on_delete=models.CASCADE, related_name="location")
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.profile.user.username}'s location"