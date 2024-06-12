from django.urls import path, include
from rest_framework.routers import DefaultRouter

from cartas_app.api.views import JugadorAV, JugadorDV, EquipoAV, ComentarioCreate, ComentarioList, ComentarioDetalle, \
    JugadorUsuarioView

router = DefaultRouter()
router.register('equipos', EquipoAV, basename='equipo')  # basename='equipo' es opcional
router.register('jugadores', JugadorAV, basename='jugador')  # basename='jugador' es opcional
urlpatterns = [

    path('jugador/<int:pk>/', JugadorDV.as_view(), name='jugador-detalle'),

    # Crear comentario de un jugador apartir de su id
    path('jugador/<int:pk>/comentario-create', ComentarioCreate.as_view(), name='comentario-create'),
    # Listar comentarios de un jugador apartir de su id
    path('jugador/<int:pk>/comentarios/', ComentarioList.as_view(), name='comentarios'),
    # detalle de un comentario por su id
    path('comentarioById/<int:pk>', ComentarioDetalle.as_view(), name='comentarioById'),

    path('usuarios/<str:username>/jugadores/', JugadorUsuarioView.as_view(), name='jugador-usuario'),

    path('', include(router.urls)),
]
