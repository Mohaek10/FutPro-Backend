from rest_framework import status, generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError

from cartas_app.models import Jugador, JugadorUsuario
from ventas_app.models import Venta
from ventas_app.api.serializers import CompraSerializer, VentaSerializer


class ComprarJugador(generics.CreateAPIView):
    serializer_class = CompraSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        jugador = serializer.validated_data.get('jugador')
        cantidad = serializer.validated_data.get('cantidad')
        usuario = self.request.user
        costo_total = jugador.valor * cantidad

        if usuario.futcoins < costo_total:
            raise ValidationError("No tienes suficientes futcoins para comprar este jugador.")

        usuario.futcoins -= costo_total
        usuario.save()

        # Verificar si el jugador ya está en la colección del usuario
        jugador_usuario, created = JugadorUsuario.objects.get_or_create(usuario=usuario, jugador=jugador)
        if not created:
            jugador_usuario.cantidad += cantidad
            jugador_usuario.save()
        else:
            serializer.save(usuario=usuario, cantidad=cantidad)


class VenderJugador(generics.CreateAPIView):
    serializer_class = VentaSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        jugador_usuario = serializer.validated_data.get('jugador_usuario')
        precio = serializer.validated_data.get('precio')
        vendedor = self.request.user

        if jugador_usuario.usuario != vendedor:
            raise ValidationError("No puedes vender un jugador que no posees.")

        if jugador_usuario.cantidad < 1:
            raise ValidationError("No tienes suficientes jugadores para vender.")

        comprador = serializer.validated_data.get('comprador')
        if vendedor == comprador:
            raise ValidationError("No puedes comprarte a ti mismo.")

        if comprador.futcoins < precio:
            raise ValidationError("El comprador no tiene suficientes futcoins.")

        # Realizar la transacción
        comprador.futcoins -= precio
        comprador.save()

        vendedor.futcoins += precio
        vendedor.save()

        jugador_usuario.cantidad -= 1
        if jugador_usuario.cantidad == 0:
            jugador_usuario.delete()
        else:
            jugador_usuario.save()

        # Registrar la venta
        Venta.objects.create(vendedor=vendedor, comprador=comprador, jugador_usuario=jugador_usuario, precio=precio)
