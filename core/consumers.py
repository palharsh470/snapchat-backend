import json
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from .models import Chat, Messages

class ChatConsumer(WebsocketConsumer):
    def connect(self):
        print("QUERY:", self.scope.get("query_string"))
        print("COOKIES:", self.scope.get("cookies"))
        print("USER:", self.scope.get("user"))
        self.user = self.scope["user"]

        if not self.user.is_authenticated:
            print("Anonymous user rejected")
            self.close()
            return

        self.chat_id = self.scope["url_route"]["kwargs"]["chat_id"]

        try:
            self.chat = Chat.objects.get(id=self.chat_id)
        except Chat.DoesNotExist:
            print("Chat does not exist")
            self.close()
            return

        if self.user not in [self.chat.user1, self.chat.user2]:
            print("User not part of this chat")
            self.close()
            return

        self.room_group_name = f"chat_{self.chat_id}"

        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name,
        )

        print(f"{self.user} joined {self.room_group_name}")

        self.accept()
    def disconnect(self, close_code):

        if hasattr(self, "room_group_name"):
            async_to_sync(self.channel_layer.group_discard)(
                self.room_group_name,
                self.channel_name
            )


    def chat_message(self, event):
        self.send(text_data=json.dumps({
            "id": event["id"],
            "text": event.get("text", ""),
            "snap": event.get("snap", ""),
            "sender": event["sender"],
            "created_at": event["created_at"],
            "is_system": event.get("is_system", False),
        }))