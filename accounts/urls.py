from .views import Login_view, Register_view, LogoutView, InfoView
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView


urlpatterns = [
    path('login/', Login_view.as_view() , name="login"), 
    path('info/', InfoView.as_view() , name="info"), 
    path('register/', Register_view.as_view() , name="register"), 
    path('logout/', LogoutView.as_view() , name="logout"), 
    path('token/refresh/', TokenRefreshView.as_view() , name="refresh-token"), 
] 


