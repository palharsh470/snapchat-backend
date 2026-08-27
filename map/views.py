from rest_framework import generics, mixins, permissions
from rest_framework.response import Response
from .models import Location
from .serializers import LocationSerializer
from core.models import FriendRequest
from django.db.models import Q

class LocationView(
    mixins.ListModelMixin, mixins.CreateModelMixin, generics.GenericAPIView
    ):

    serializer_class = LocationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_context(self):
        return {"request": self.request}

    def get_friend_user_ids(self):
        user = self.request.user

        accepted = FriendRequest.objects.filter(
            Q(from_user=user) | Q(to_user=user),
            status=FriendRequest.StatusChoices.ACCEPTED,
        )

        friend_ids = set()
        for req in accepted:
            friend_ids.add(
                req.to_user_id if req.from_user_id == user.id else req.from_user_id
            )

        return friend_ids

    def get_queryset(self):
        friend_ids = self.get_friend_user_ids()

        return Location.objects.filter(
            profile__user_id__in=friend_ids,
            latitude__isnull=False,
            longitude__isnull=False,
        ).select_related("profile__user")

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        profile = request.user.profile
        location, _ = Location.objects.update_or_create(
            profile=profile,
            defaults={
                "latitude": request.data.get("latitude"),
                "longitude": request.data.get("longitude"),
            },
        )
        serializer = self.get_serializer(location)
        return Response(serializer.data)
