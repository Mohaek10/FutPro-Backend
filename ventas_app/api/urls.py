from django.urls import path, include
from rest_framework.routers import DefaultRouter

from ventas_app.api.views import JugadorUsuarioViewSet

router = DefaultRouter()
router.register(r'jugadorusuario', JugadorUsuarioViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
