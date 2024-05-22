from django.urls import path, include
from rest_framework.routers import DefaultRouter

from cartas_app.api.views import JugadorAV, JugadorDV, EquipoAV

router = DefaultRouter()
router.register('equipos', EquipoAV, basename='equipos')
urlpatterns = [
    path('jugadores/', JugadorAV.as_view(), name='jugadores'),
    path('jugadores/<int:pk>', JugadorDV.as_view(), name='jugador-detalle'),

    path('', include(router.urls)),
]
