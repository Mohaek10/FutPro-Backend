from rest_framework import viewsets, status
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError

from cartas_app.api.serializers import JugadorUsuarioSerializer
from cartas_app.models import Jugador, JugadorUsuario


class JugadorUsuarioViewSet(viewsets.ModelViewSet):
    queryset = JugadorUsuario.objects.all()
    serializer_class = JugadorUsuarioSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        usuario = request.user
        jugador_id = request.data.get('jugador')
        cantidad = int(request.data.get('cantidad', 1))

        jugador = get_object_or_404(Jugador, id=jugador_id)

        if not jugador.isActive:
            raise ValidationError("Este jugador no está disponible para la compra")

        jugador_usuario, created = JugadorUsuario.objects.get_or_create(usuario=usuario, jugador=jugador)
        if not created:
            jugador_usuario.cantidad += cantidad
        else:
            jugador_usuario.cantidad = cantidad
        jugador_usuario.save()

        serializer = self.get_serializer(jugador_usuario)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
