from django.urls import path, include

from cartas_app.api.views import JugadorAV, JugadorDV

urlpatterns = [
    path('jugadores/', JugadorAV.as_view(), name='jugadores'),
    path('jugadores/<int:pk>', JugadorDV.as_view(), name='jugador-detalle'),
]
