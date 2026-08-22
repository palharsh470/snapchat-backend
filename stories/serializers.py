from rest_framework import serializers
from django.utils import timezone
from datetime import timedelta
from .models import Story
from django.contrib.auth.models import User

class StorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Story
        fields = ["id", "attachment", "created_at"]

class StoryUserSerializer(serializers.ModelSerializer):
    profile = serializers.SerializerMethodField()
    stories = serializers.SerializerMethodField()
    class Meta :
        model = User
        fields = ["id",
                    "profile",
                    "stories",
                    "username"]
    def get_stories(self, obj):
            last_24_hours =timezone.now() - timedelta(hours=24)
            stories = obj.stories.filter( created_at__gte=last_24_hours).order_by("created_at")
    
            return StorySerializer(
                stories,
                many=True,
                context=self.context
            ).data

    def get_profile(self, obj):
        from core.serializers import ProfileSerializer

        return ProfileSerializer(
            obj.profile,
            context=self.context
        ).data
         