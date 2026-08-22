from django.shortcuts import render
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from rest_framework.response import Response
from .serializers import StorySerializer, StoryUserSerializer
from django.db.models import Q
from rest_framework import status


class StoriesView(GenericAPIView):
    serializer_class = StorySerializer
    permission_classes = [IsAuthenticated]

    def get(self, request):
        users = User.objects.filter(
            Q(stories__isnull=False)
            & Q(stories__created_at__gte=timezone.now() - timedelta(hours=24))
        ).distinct()
        serializer = StoryUserSerializer(users, many=True, context={"request": request})
        return Response(
            {"status": True, "data": serializer.data}, status=status.HTTP_200_OK
        )

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        return Response(
            {"status": True, "message": "Story Added Successfully"},
            status=status.HTTP_201_CREATED,
        )
