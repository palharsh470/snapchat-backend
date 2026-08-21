from django.contrib import admin
from django.contrib.auth.models import User
from .models import Profile, FriendRequest, Chat, Messages, Story, Spotlight, Like


admin.site.register(Profile)
admin.site.register(FriendRequest)
admin.site.register(Chat)
admin.site.register(Messages)
admin.site.register(Story)
admin.site.register(Spotlight)
admin.site.register(Like)