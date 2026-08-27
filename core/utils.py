from .models import FriendRequest
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta
import json
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

def broadcast_message(msg):
    channel_layer = get_channel_layer()
    snap_url = ""

    if msg.snap:
        snap_url = f"http://10.95.161.5:8000{msg.snap.url}"
    async_to_sync(channel_layer.group_send)(
        f"chat_{msg.chat.id}",
        {
            "type": "chat.message",
            "id": msg.id,
            "text": msg.text,
            "snap": snap_url,
            "sender": msg.sender.id,
            "created_at": msg.created_at.strftime("%H:%M"),
            "is_system": msg.is_system,
        },
    )

def chat_message(self, event):
        self.send(text_data=json.dumps({
            "id": event["id"],
            "text": event["text"],
            "snap": event["snap"],
            "sender": event["sender"],
            "created_at": event["created_at"],
            "is_system": event["is_system"],
        }))

def get_friends(user):
    unique_friends = set()
    queryset = FriendRequest.objects.filter(
            Q(from_user=user) | Q(to_user=user)
            )
    friends = queryset.filter(status=FriendRequest.StatusChoices.ACCEPTED)
    
    for friend in friends:
        if user == friend.from_user:
            unique_friends.add(friend.to_user)
        else:
            unique_friends.add(friend.from_user)

    return unique_friends

def get_friends_28days_count(user):
    unique_friends = set()

    queryset = FriendRequest.objects.filter(
            Q(from_user=user) | Q(to_user=user)
            )
    friends = queryset.filter(Q(status=FriendRequest.StatusChoices.ACCEPTED) & Q(updated_at__gte = timezone.now() - timedelta(days=28)))
    
    for friend in friends:
        if user == friend.from_user:
            unique_friends.add(friend.to_user)
        else:
            unique_friends.add(friend.from_user)

    return len(unique_friends)

def pending_friends(user):
    pending = []
    queryset = FriendRequest.objects.filter(
                Q(from_user=user) | Q(to_user=user)
            )
    pending_requests = queryset.filter(status=FriendRequest.StatusChoices.PENDING)


    for req in pending_requests:
        if user == req.from_user:
            pending.append(req.to_user.id)
        else:
            pending.append(req.from_user.id)

    return pending


def are_friends(user1, user2):
    is_friend = FriendRequest.objects.filter(
        Q(from_user=user1, to_user=user2)
        | Q(from_user=user2, to_user=user1)
    ).filter(status = FriendRequest.StatusChoices.ACCEPTED).exists()

    return is_friend