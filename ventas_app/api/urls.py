from django.urls import path
from ventas_app.api.views import ComprarJugador, VenderJugador

urlpatterns = [
    path('comprar/', ComprarJugador.as_view(), name='comprar-jugador'),
    path('vender/', VenderJugador.as_view(), name='vender-jugador'),
]
