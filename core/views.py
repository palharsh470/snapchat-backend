from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from .serializers import (
    UserSerializer,
    FriendRequestSerializer,
    ProfileEditSerializer,
    ProfileSerializer,
    SpotlightSerializer,
    StorySerializer,
    UserEditSerializer,
    ChatSerailizer,
    MessageSerializer,
    UserFriendSerializer
)
from .pagination import SpotlightPagination
from stories.models import Story
from rest_framework.parsers import MultiPartParser, FormParser
from django.contrib.auth.models import User
from rest_framework.permissions import IsAuthenticated
from .models import FriendRequest, Profile, Spotlight, Like, Chat
from django.shortcuts import get_object_or_404
from django.db.models import Q
from rest_framework import status
from rest_framework.views import APIView
from .utils import get_friends, get_friends_28days_count, broadcast_message
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.models import User


class ChatView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    def get(self, request):
        friends = get_friends(request.user)
        serializer = self.get_serializer(friends, many=True)
        return Response(
            {"status": True, "data": serializer.data}, status=status.HTTP_200_OK
        )


class SendRequestView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, id):
        if request.user.id == id:
            return Response(
                {
                    "status": False,
                    "message": "You cannot send a friend request to yourself.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        is_exist = FriendRequest.objects.filter(
            Q(from_user__id=request.user.id, to_user__id=id)
            | Q(from_user__id=id, to_user__id=request.user.id)
        ).exists()

        if is_exist:
            return Response(
                {"status": False, "message": "Request Already sent"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        friend = get_object_or_404(User, id=id)
        FriendRequest.objects.create(from_user=request.user, to_user=friend)
        return Response(
            {"status": True, "message": "Request send sucessfully"},
            status=status.HTTP_201_CREATED,
        )


class AcceptRequestView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, id):
        friend_request = get_object_or_404(FriendRequest, id=id)
        print(friend_request.from_user, "from")
        print(friend_request.to_user, "to")
        if friend_request.to_user != request.user:
            return Response(
                {"status": False, "message": "Unauthorized"},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        if friend_request.status == "accepted":
            return Response(
                {"status": False, "message": "You are already Friends"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        friend_request.status = FriendRequest.StatusChoices.ACCEPTED
        friend_request.save()
        return Response(
            {"status": True, "message": "You are now Friends"},
            status=status.HTTP_201_CREATED,
        )


class UsersView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    def get(self, request):
        users = User.objects.exclude(id=request.user.id)

        search = request.query_params.get("search", "").strip()
        if search:
            users = users.filter(username__icontains=search)

        serializer = self.get_serializer(users, many=True)
        return Response(
            {"status": True, "data": serializer.data}, status=status.HTTP_200_OK
        )



class ProfileEditView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def patch(self, request):

        profile_instance = get_object_or_404(Profile, id=request.user.profile.id)

        profile_serializer = ProfileEditSerializer(
            instance=profile_instance, data=request.data, partial=True
        )
        user_serializer = UserEditSerializer(
            instance=request.user, data=request.data, partial=True
        )
        profile_serializer.is_valid(raise_exception=True)
        user_serializer.is_valid(raise_exception=True)
        profile_serializer.save()
        user_serializer.save()

        return Response(
            {"status": True, "data": profile_serializer.data},
            status=status.HTTP_200_OK,
        )


class ProfileView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, id):
        profile_info = Profile.objects.filter(user__id=id).first()

        if not profile_info:
            return Response(
                {"status": False, "message": "Profile not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        user_story = Story.objects.filter(user__id=id)

        user_spotlight = Spotlight.objects.filter(user__id=id)

        last_28days = timezone.now() - timedelta(days=28)

        story_count_28days = user_story.filter(created_at__gte=last_28days).count()

        spotlight_count_28days = user_spotlight.filter(
            created_at__gte=last_28days
        ).count()

        friends = get_friends(profile_info.user)
        friends_count = len(friends)

        profile_serializer = ProfileSerializer(
            profile_info, context={"request": request}
        )
        user_serializer = UserSerializer(
            profile_info.user, context={"request": request}
        )
        friends_serializer = UserFriendSerializer(
            friends, context={"request": request}, many=True
        )

        story_serializer = StorySerializer(
            user_story, many=True, context={"request": request}
        )

        spotlight_serializer = SpotlightSerializer(
            user_spotlight, many=True, context={"request": request}
        )

        return Response(
            {
                "status": True,
                "data": {
                    "profileInfo": profile_serializer.data if profile_info else None,
                    "userInfo": user_serializer.data,
                    "stories": story_serializer.data,
                    "spotlights": spotlight_serializer.data,
                    "friendsCount": friends_count,
                    "friends" : friends_serializer.data,
                    "friendsCount28days": get_friends_28days_count(profile_info.user),
                    "storyCount28days": story_count_28days,
                    "spotlightCount28days": spotlight_count_28days,
                },
            },
            status=status.HTTP_200_OK,
        )




class SpotlightView(GenericAPIView):
    serializer_class = SpotlightSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = SpotlightPagination
    
    def get(self, request):
        spotlight = Spotlight.objects.all().order_by("-id")
        page = self.paginate_queryset(spotlight)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        return Response(
            {"status": True, "message": "Spotlight Added Successfully"},
            status=status.HTTP_201_CREATED,
        )


class PendingRequestView(GenericAPIView):
    serializer_class = FriendRequestSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request):
        pending_request = FriendRequest.objects.filter(
            Q(to_user=request.user) & Q(status=FriendRequest.StatusChoices.PENDING)
        )
        serializer = self.get_serializer(pending_request, many=True)
        return Response(
            {"status": True, "data": serializer.data}, status=status.HTTP_200_OK
        )


class LikeSpotlightView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, id):
        spotlight = get_object_or_404(Spotlight, pk=id)
        user = request.user
        isLiked = Like.objects.filter(Q(user=user) & Q(spotlight=spotlight)).first()
        if isLiked:
            isLiked.delete()
            return Response(
                {"status": True, "message": f"{request.user} unlikes the Spotlight"},
                status=status.HTTP_200_OK,
            )
        else:
            Like.objects.create(user=user, spotlight=spotlight)

        return Response(
            {"status": True, "message": f"{request.user} likes the Spotlight"},
            status=status.HTTP_200_OK,
        )


class ChatDetailsView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ChatSerailizer
    def get(self, request, id):
        friend = get_object_or_404(User, pk=id)
        
        Chat.objects.filter(expires_at__lte=timezone.now()).delete()
        chatRoom = Chat.objects.filter(Q(user1=request.user, user2=friend) | Q(user1=friend, user2=request.user)).first()
        if chatRoom is None:
            chatRoom = Chat.objects.create(
                user1=request.user,
                user2=friend,
                streak=0,
                last_message=timezone.now(),
                updated_at=timezone.now(),
            )

        if chatRoom.user2.id == request.user.id:
            chatRoom.isviewed = True
            chatRoom.viewed_at = timezone.now()

            if chatRoom.mode == "on_close":
                chatRoom.expires_at = timezone.now()

            if chatRoom.mode == "after_24_hr":
                chatRoom.expires_at = timezone.now() + timedelta(hours=24)

            chatRoom.save()

        serializer = self.get_serializer(chatRoom)
        
        return Response(
            {"status": True,   "data": serializer.data},
            status=status.HTTP_200_OK,
        )

    def patch(self, request, id):
        friend = get_object_or_404(User, pk=id)

        chatRoom = Chat.objects.filter(
            Q(user1=request.user, user2=friend) |
            Q(user1=friend, user2=request.user)
        ).first()

        if not chatRoom:
            return Response(
                 { "status" : False,
                    "message": "Chat room not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = self.get_serializer(
            chatRoom,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():
            serializer.save()
            return Response({
                "status" : True,
                "data" : serializer.data
            }, status=status.HTTP_206_PARTIAL_CONTENT)

        return Response(
            {
                "status" : False,
                "message" : serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )

class MessageView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = MessageSerializer

    def post(self, request, id):
        chatRoom = get_object_or_404(Chat, id=id)

        sender = request.user

        if chatRoom.user1.id == sender.id:
            receiver = chatRoom.user2
        else:
            receiver = chatRoom.user1

        is_system = bool(request.data.get("screenshot"))

        data = {
            "text": request.data.get("text", ""),
            "sender": sender.id,
            "receiver": receiver.id,
            "is_system": is_system,
        }

        if "snap" in request.FILES:
            data["snap"] = request.FILES["snap"]

        serializer = self.get_serializer(data=data)

        serializer.is_valid(raise_exception=True)

        message = serializer.save(chat=chatRoom)

        broadcast_message(message)
        return Response({
            "status" : True,
            "data" : serializer.data
        },
            status=status.HTTP_201_CREATED
        )

        
        
