import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")
from core.middleware import JWTAuthMiddleware
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator

from core.routing import websocket_urlpatterns
print("🔥 ASGI FILE LOADED")
django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter({

    "http": django_asgi_app,

    "websocket": AllowedHostsOriginValidator(
        JWTAuthMiddleware(
            URLRouter(websocket_urlpatterns)
        )
    ),

})