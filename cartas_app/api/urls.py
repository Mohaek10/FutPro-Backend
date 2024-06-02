from django.urls import path, include
from rest_framework.routers import DefaultRouter

from cartas_app.api.views import JugadorAV, JugadorDV, EquipoAV, ComentarioCreate, ComentarioList, ComentarioDetalle, \
    JugadorUsuarioView

router = DefaultRouter()
router.register('equipos', EquipoAV, basename='equipo')  # basename='equipo' es opcional
urlpatterns = [
    path('jugadores/', JugadorAV.as_view(), name='jugadores'),
    path('jugadores/<int:pk>', JugadorDV.as_view(), name='jugador-detalle'),

    # Crear comentario de un jugador apartir de su id
    path('jugador/<int:pk>/comentario-create', ComentarioCreate.as_view(), name='comentario-create'),
    # Listar comentarios de un jugador apartir de su id
    path('jugador/<int:pk>/comentarios/', ComentarioList.as_view(), name='comentarios'),
    path('comentarioById/<int:pk>', ComentarioDetalle.as_view(), name='comentarioById'),

    path('usuarios/<str:username>/jugadores/', JugadorUsuarioView.as_view(), name='jugador-usuario'),

    path('', include(router.urls)),
]
