from django.shortcuts import get_object_or_404
from rest_framework import status, generics
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework.views import APIView

from cartas_app.models import Jugador, JugadorUsuario
from ventas_app.api.serializers import MercadoSistemaSerializer, CompraSistemaSerializer, VentaUsuarioSerializer
from ventas_app.models import VentaUsuario


# Vista para ver los jugadores en el mercado del sistema, que tienen en_mercado=True
class MercadoSistemaList(generics.ListAPIView):
    serializer_class = MercadoSistemaSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return Jugador.objects.filter(en_mercado=True, isActive=True)


class ComprarMercadoSistema(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = CompraSistemaSerializer(data=request.data)

        if serializer.is_valid():
            jugador_id = serializer.validated_data.get('jugador_id')
            cantidad = serializer.validated_data.get('cantidad')
            usuario = request.user

            # Verificar que el jugador existe y está en el mercado
            jugador = get_object_or_404(Jugador, id=jugador_id, en_mercado=True, isActive=True)

            # Validar que el usuario tenga suficientes FutCoins
            costo_total = jugador.valor * cantidad
            if usuario.futcoins < costo_total:
                return Response({'error': 'No tienes suficientes FutCoins para comprar este jugador.',
                                 'futcoins': usuario.futcoins,
                                 'precioTotal': costo_total, },
                                status=status.HTTP_400_BAD_REQUEST)

            # Crear la entrada de jugador_usuario o actualizar la cantidad si ya existe
            jugador_usuario, created = JugadorUsuario.objects.get_or_create(usuario=usuario, jugador=jugador)
            if created:
                jugador_usuario.cantidad = cantidad  # Establecer la cantidad si es la primera vez que se añade
            else:
                jugador_usuario.cantidad += cantidad  # Incrementar la cantidad si ya existe
            jugador_usuario.save()

            # Descontar los FutCoins del usuario
            usuario.futcoins -= costo_total
            usuario.save()
            data = {'success': 'Jugador comprado exitosamente.',
                    'futcoins': usuario.futcoins,
                    'jugador': jugador.nombreCompleto,
                    'precioTotal': costo_total, }
            return Response(data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MercadoUsuariosList(generics.ListAPIView):
    serializer_class = VentaUsuarioSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return VentaUsuario.objects.filter(isActive=True)


# Vista para poner un jugador en venta
class PonerEnVentaUsuario(generics.CreateAPIView):
    serializer_class = VentaUsuarioSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        jugador_usuario = serializer.validated_data.get('jugador_usuario')
        precio = serializer.validated_data.get('precio')
        vendedor = self.request.user

        # Verificar que el jugador_usuario pertenece al vendedor
        if jugador_usuario.usuario != vendedor:
            raise ValidationError({'error': 'No puedes vender un jugador que no posees.'})

        # Verificar que el vendedor no está poniendo en venta más jugadores de los que posee
        total_en_venta = VentaUsuario.objects.filter(vendedor=vendedor, jugador_usuario=jugador_usuario,
                                                     isActive=True).count()
        if total_en_venta >= jugador_usuario.cantidad:
            raise ValidationError({'error': 'No puedes poner en venta más jugadores de los que posees.'})

        # Crear la entrada de venta
        serializer.save(vendedor=vendedor, jugador_usuario=jugador_usuario)


class ComprarJugadorUsuario(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, venta_id):
        venta = get_object_or_404(VentaUsuario, id=venta_id, isActive=True)
        comprador = self.request.user

        if comprador.futcoins < venta.precio:
            return Response({'error': 'No tienes suficientes FutCoins para comprar este jugador.'},
                            status=status.HTTP_400_BAD_REQUEST)

        vendedor = venta.vendedor
        jugador_usuario = venta.jugador_usuario

        # Verificar que el jugador está disponible
        if jugador_usuario.cantidad < 1:
            return Response({'error': 'El jugador ya no está disponible.'}, status=status.HTTP_400_BAD_REQUEST)

        # Transferir FutCoins
        comprador.futcoins -= venta.precio
        comprador.save()

        vendedor.futcoins += venta.precio
        vendedor.save()

        # Transferir la propiedad del jugador
        jugador_usuario.usuario = comprador
        jugador_usuario.save()

        # Marcar la venta como inactiva
        venta.isActive = False
        venta.save()

        return Response({'success': 'Jugador comprado exitosamente.'}, status=status.HTTP_200_OK)


class EliminarJugadorDelMercado(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, venta_id):
        venta = get_object_or_404(VentaUsuario, id=venta_id, isActive=True)
        vendedor = self.request.user

        # Verificar que el vendedor es el dueño de la venta
        if venta.vendedor != vendedor:
            return Response({'error': 'No tienes permiso para eliminar esta venta.'},
                            status=status.HTTP_403_FORBIDDEN)

        # Incrementar la cantidad del jugador en la relación JugadorUsuario
        jugador_usuario = venta.jugador_usuario
        jugador_usuario.cantidad += 1
        jugador_usuario.save()

        # Marcar la venta como inactiva
        venta.isActive = False
        venta.save()

        return Response({'success': 'Venta eliminada exitosamente.'}, status=status.HTTP_200_OK)
