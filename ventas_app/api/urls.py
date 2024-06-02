from django.urls import path
from ventas_app.api.views import PonerEnVentaUsuario, MercadoUsuariosList, ComprarJugadorUsuario, MercadoSistemaList, \
    ComprarMercadoSistema, EliminarJugadorDelMercado, TransaccionesUsuarioList, TransaccionesAdminList

urlpatterns = [
    # path del mercado del sistema
    path('mercado-sistema/', MercadoSistemaList.as_view(), name='mercado-sistema'),
    path('comprar-sistema/', ComprarMercadoSistema.as_view(), name='comprar-sistema'),

    # paths del mercado de usuarios
    path('poner-en-venta/', PonerEnVentaUsuario.as_view(), name='poner-en-venta-usuario'),
    path('mercado-usuarios/', MercadoUsuariosList.as_view(), name='mercado-usuarios'),
    path('comprar-usuario/<int:venta_id>/', ComprarJugadorUsuario.as_view(), name='comprar-jugador-usuario'),
    path('eliminar-venta/<int:venta_id>/', EliminarJugadorDelMercado.as_view(), name='eliminar-venta-usuario'),

    path('transacciones-usuario/', TransaccionesUsuarioList.as_view(), name='transacciones-usuario'),
    path('transacciones-admin/', TransaccionesAdminList.as_view(), name='transacciones-admin')
]
