from django.db import models
from django.contrib.auth.models import User

class Story(models.Model):
    user = models.ForeignKey(to=User, on_delete=models.CASCADE, related_name="stories")
    attachment = models.ImageField(upload_to="story")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} 's story"