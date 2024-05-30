from django.urls import path, include
from rest_framework.routers import DefaultRouter

from cartas_app.api.views import JugadorAV, JugadorDV, EquipoAV, ComentarioCreate, ComentarioList

router = DefaultRouter()
router.register('equipos', EquipoAV, basename='equipos')
urlpatterns = [
    path('jugadores/', JugadorAV.as_view(), name='jugadores'),
    path('jugadores/<int:pk>', JugadorDV.as_view(), name='jugador-detalle'),

    # Crear comentario de un jugador apartir de su id
    path('jugador/<int:pk>/comentario-create', ComentarioCreate.as_view(), name='comentario-create'),
    # Listar comentarios de un jugador apartir de su id
    path('jugador/<int:pk>/comentarios/', ComentarioList.as_view(), name='comentarios'),

    path('', include(router.urls)),
]
