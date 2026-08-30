from rest_framework import serializers
from django.contrib.auth.models import User
from .models import FriendRequest, Profile, Spotlight, Chat, Messages
from django.db.models import Q
from .utils import are_friends
from django.utils import timezone
from datetime import timedelta
from stories.serializers import StorySerializer
from backend import settings

class UserEditSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "email",
        ]

class ProfileEditSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = [
            "dob",
            "mobile",
            "private",
            "image",
            "avatar",
        ]
    

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = [
            "id",
            "image",
            "avatar",
            "dob",
            "mobile",
            "private",
        ]

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep["image"] = f"{settings.BACKEND_BASE_URL}{instance.image.url}" if instance.image else None
        rep["avatar"] = f"{settings.BACKEND_BASE_URL}{instance.avatar.url}" if instance.avatar else None
        return rep


class UserSerializer(serializers.ModelSerializer):
    friend_request_status = serializers.SerializerMethodField()
    friend_request_id = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()
    profile = ProfileSerializer()
    stories = StorySerializer(many=True)
    class Meta:
        model = User
        fields = [
            "id",
            "profile",
            "username",
            "first_name",
            "last_name",
            "email",
            "stories",
            "last_message",
            "friend_request_status",
            "friend_request_id",
        ]

    def get_last_message(self, obj):
        current_user = self.context["request"].user
        message = Messages.objects.filter(Q(sender=obj, receiver=current_user) | Q(sender=current_user, receiver=obj)).order_by("created_at").last()
        if not message:
            return None
        if message.snap :  
            return {
                "snap": "snap",
                "timestamp": message.created_at,
            }
        else :
            return {
                "text": message.text,
                "timestamp": message.created_at,
            }

    def get_friend_request_id(self, obj):
        current_user = self.context["request"].user
        if current_user == obj :
            return None
        friend_request = FriendRequest.objects.filter(
                    Q(from_user=current_user, to_user=obj)
                    | Q(to_user=current_user, from_user=obj)
                ).first()

        if friend_request :
            return friend_request.id
        else :
            return None
        

    def get_friend_request_status(self, obj):
        current_user = self.context["request"].user
        if current_user == obj :
            return None

        friend_request = FriendRequest.objects.filter(
            Q(from_user=current_user, to_user=obj)
            | Q(to_user=current_user, from_user=obj)
        ).first()

        if not friend_request:
            return "not_friends"
        
        if friend_request.from_user == current_user and friend_request.status == "pending":
            return "pending"
        
        if  friend_request.status == "accepted":
            return "friends"

        return "accept_request"

class ProfileImageSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = Profile  
        fields = ["image"]

    def get_image(self, obj):
        if obj.image:
            return f"{settings.BACKEND_BASE_URL}{obj.image.url}"
        return None



class UserFriendSerializer(serializers.ModelSerializer):
    profile = ProfileImageSerializer()

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "profile",
            "first_name",
            "last_name",
        ]

class SpotlightProfileSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = [
            "image",
        ]

    def get_image(self, obj):
        if obj.image:
            return f"{settings.BACKEND_BASE_URL}{obj.image.url}"
        return None

class SpotlightUserSerializer(serializers.ModelSerializer):
    profile = SpotlightProfileSerializer()
    is_friend = serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "profile",
            "is_friend"
        ]
    def get_is_friend(self, obj):
        current_user = self.context["request"].user
        if obj == current_user :
            return None
        return are_friends(obj, current_user)


class SpotlightSerializer(serializers.ModelSerializer):
    likes = serializers.SerializerMethodField()
    isLiked = serializers.SerializerMethodField()
    user = SpotlightUserSerializer(read_only = True)
    class Meta:
        model = Spotlight
        fields = [
            "id",
            "caption",
            "upload",
            "user",
            "likes",
            "isLiked",
            "created_at"
        ]

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep["upload"] = f"{settings.BACKEND_BASE_URL}{instance.upload.url}" if instance.upload else None
        return rep

    def get_likes(self, obj):
        return obj.spotlight_likes.count()

    def get_isLiked(self, obj):
        request = self.context.get("request")

        if not request or not request.user.is_authenticated:
            return False

        return obj.spotlight_likes.filter(
            user=request.user
        ).exists()

class FriendRequestSerializer(serializers.ModelSerializer):
    from_user = UserSerializer()
    class Meta:
        model = FriendRequest
        fields = ["id", "to_user", "from_user", "status", "created_at", "updated_at"]

class ChatUserSerializer(serializers.ModelSerializer):
    profile = SpotlightProfileSerializer()
    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "profile",
        ]

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Messages
        fields = [
            "id",
            "chat",
            "sender",
            "receiver",
            "text",
            "created_at",
            "snap",
            "is_system",
        ]
        read_only_fields = ["chat"]

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep["snap"] = f"{settings.BACKEND_BASE_URL}{instance.snap.url}" if instance.snap else None
        return rep
        
 
class ChatSerailizer(serializers.ModelSerializer):
    user1 = ChatUserSerializer()
    user2 = ChatUserSerializer()
    messages = serializers.SerializerMethodField()
    class Meta :
        model = Chat
        fields = [ "id", "user1", "user2", "mode", "streak", "viewed_at", "expires_at", "last_message", "isviewed" , "messages" ]


    def get_messages(self, obj):
        messages = obj.messages.all().order_by("-created_at")

        return MessageSerializer(
            messages,
            many=True,
            context=self.context
        ).data