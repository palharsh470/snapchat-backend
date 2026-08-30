from rest_framework import serializers
from django.utils import timezone
from datetime import timedelta
from django.conf import settings
from .models import Story
from django.contrib.auth.models import User

from django.conf import settings

class StorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Story
        fields = ["id", "attachment", "created_at"]

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        if instance.attachment:
            rep["attachment"] = f"{settings.BACKEND_BASE_URL}{instance.attachment.url}"
        else:
            rep["attachment"] = None
        return rep

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