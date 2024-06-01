from django.urls import path
from ventas_app.api.views import PonerEnVentaUsuario, MercadoUsuariosList, ComprarJugadorUsuario

urlpatterns = [
    path('poner-en-venta/', PonerEnVentaUsuario.as_view(), name='poner-en-venta-usuario'),
    path('mercado-usuarios/', MercadoUsuariosList.as_view(), name='mercado-usuarios'),
    path('comprar-usuario/<int:venta_id>/', ComprarJugadorUsuario.as_view(), name='comprar-jugador-usuario'),
]
