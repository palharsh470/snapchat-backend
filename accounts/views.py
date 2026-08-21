from rest_framework.views import APIView
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import RegisterSerializer
from rest_framework.generics import GenericAPIView
from django.contrib.auth import login
from rest_framework.permissions import IsAuthenticated
from core.models import Profile


class Login_view(APIView):
    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        user = authenticate(username=username, password=password)

        if user is None:
            return Response(
                {"status": False, "message": "Invalid username or password"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        login(request, user)
        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "status": True,
                "data": {"id": user.id, "username": user.username, "email": user.email},
                "tokens": {
                    "access": str(refresh.access_token),
                    "refresh": str(refresh),
                },
                "message": "Login Successfully",
            },
            status=status.HTTP_200_OK,
        )

class InfoView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        return Response({
            "status": True,
            "data": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
            }
        }, status=status.HTTP_200_OK)

class Register_view(GenericAPIView):

    serializer_class = RegisterSerializer

    def post(self, request):

        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()
            Profile.objects.get_or_create(user = user)
            return Response(
                {"status": True, "message": "User Created Successfully"},
                status=status.HTTP_201_CREATED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
      
            refresh_token = request.data.get("refresh")
            print(refresh_token)
            if not refresh_token:
                return Response(
                    {"status": False, "message": "Refresh token is required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response(
                {"status": True, "message": "Logout successful"},
                status=status.HTTP_200_OK,
            )

        except Exception:
            return Response(
                {"status": False, "message": "Invalid refresh token"},
                status=status.HTTP_400_BAD_REQUEST,
            )
