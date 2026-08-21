from rest_framework import serializers
from django.contrib.auth.models import User
from .models import FriendRequest, Profile, Story, Spotlight, Like, Chat, Messages
from django.db.models import Q
from .utils import are_friends


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
            "longitude",
            "latitude",
        ]





class StorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Story
        fields = ["id", "attachment", "created_at"]

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = [
            "id",
            "image",
            "avatar",
            "dob",
            "mobile",
            "longitude",
            "latitude",
            "private",
        ]


class UserSerializer(serializers.ModelSerializer):
    friend_request_status = serializers.SerializerMethodField()
    friend_request_id = serializers.SerializerMethodField()
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
            "friend_request_status",
            "friend_request_id",
        ]

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

class SpotlightProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = [
            "image",
        ]


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
    user = SpotlightUserSerializer()
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
        
 
class ChatSerailizer(serializers.ModelSerializer):
    user1 = ChatUserSerializer()
    user2 = ChatUserSerializer()
    messages = MessageSerializer(many=True)
    class Meta :
        model = Chat
        fields = [ "id", "user1", "user2", "mode", "streak", "viewed_at", "expires_at", "last_message", "isviewed" , "messages" ]

