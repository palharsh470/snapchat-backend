from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model

class Profile(models.Model):
    user = models.OneToOneField(to=User, on_delete=models.CASCADE, related_name="profile")
    dob = models.DateField(blank=True, null=True)
    mobile = models.PositiveIntegerField(blank=True, null=True)
    private = models.BooleanField(default=False)
    image = models.ImageField(upload_to="profile_image", default="avatar/default-avatar.jpg", blank=True, null=True)
    avatar = models.ImageField(upload_to="avatar",default="avatar/default-avatar.jpg", blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} 's profile"

class FriendRequest(models.Model):
    class StatusChoices(models.TextChoices):
        PENDING = "pending", "Pending"
        ACCEPTED = "accepted", "Accepted"

    from_user = models.ForeignKey(to=User, on_delete=models.CASCADE, related_name="send_requests")
    to_user = models.ForeignKey(to=User, on_delete=models.CASCADE, related_name="received_requests")
    status = models.CharField(
        max_length=10, choices=StatusChoices.choices , default=StatusChoices.PENDING
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together=("from_user", "to_user")

    def __str__(self):
        return f"{self.from_user}->{self.to_user}"

class Chat(models.Model):
    class Mode(models.TextChoices):
        KEEP = 'keep', 'Keep'
        ON_CLOSE = 'on_close', 'On_close'
        AFTER_24_HR = 'after_24_hr', 'After_24_Hr'

    user1 = models.ForeignKey(to=get_user_model(), on_delete=models.CASCADE, related_name="user1_chats")
    user2 = models.ForeignKey(to=get_user_model(), on_delete=models.CASCADE, related_name="user2_chats")
    mode = models.CharField(max_length=16, choices=Mode.choices, default=Mode.ON_CLOSE)
    streak = models.PositiveIntegerField()
    isviewed = models.BooleanField(default=False)
    viewed_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True,default=None, blank=True)
    last_message = models.DateTimeField()
    updated_at = models.DateTimeField()

    def __str__(self):
        return f"Chat : {self.user1} <-> {self.user2}"


class Messages(models.Model):
    chat = models.ForeignKey(to=Chat, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(to=User, on_delete=models.CASCADE, related_name="send_messages")
    receiver = models.ForeignKey(to=User, on_delete=models.CASCADE, related_name="received_messages")
    text = models.TextField(blank=True)
    is_system = models.BooleanField(default=False)
    snap = models.ImageField(upload_to="snaps", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender} -> {self.receiver}"


class Spotlight(models.Model):
    user = models.ForeignKey(to=User, on_delete=models.CASCADE, related_name="spotlights")
    upload = models.FileField(upload_to="videos")
    caption = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} 's spotlight"

class Like(models.Model):
    user = models.ForeignKey(to=User,on_delete=models.CASCADE, related_name="user_likes")
    spotlight = models.ForeignKey(to=Spotlight, on_delete=models.CASCADE, related_name="spotlight_likes")
    created_at = models.DateTimeField( auto_now_add=True)

    def __str__(self):
        return f"user liked {self.spotlight}"
