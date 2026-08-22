from . import views
from django.urls import path, include

urlpatterns = [
    path("chat/", views.ChatView.as_view(), name="chat"),
    path("request/sent/<int:id>/", views.SendRequestView.as_view(), name="send-request"),
    path("request/accept/<int:id>/", views.AcceptRequestView.as_view(), name="accept-request"),
    path("users/", views.UsersView.as_view(), name="users"),
    path("profile/<int:id>/", views.ProfileView.as_view(), name="profile"),
    path("profile/edit/", views.ProfileEditView.as_view(), name="profile-edit"),
    path("spotlight/", views.SpotlightView.as_view(), name="spotlight"),
    path("request/pending/", views.PendingRequestView.as_view(), name="pending-request"),
    path("spotlight/like/<int:id>/", views.LikeSpotlightView.as_view(), name="like-spotlight"),
    path("chat/friend/<int:id>/", views.ChatDetailsView.as_view(), name="friend-chats"),
    path("chat/chatroom/<int:id>/", views.MessageView.as_view(), name="chatroom-chats"),
    
]
