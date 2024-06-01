from django.shortcuts import get_object_or_404
from rest_framework import status, generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework.views import APIView

from cartas_app.models import Jugador, JugadorUsuario
from ventas_app.api.serializers import MercadoSistemaSerializer, CompraSistemaSerializer, VentaUsuarioSerializer
from ventas_app.models import VentaUsuario


class MercadoSistemaList(generics.ListAPIView):
    serializer_class = MercadoSistemaSerializer
    permission_classes = [IsAuthenticated]

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
            jugador = get_object_or_404(Jugador, id=jugador_id, en_mercado_sistema=True, isActive=True)

            # Validar que el usuario tenga suficientes FutCoins
            costo_total = jugador.valor * cantidad
            if usuario.futcoins < costo_total:
                return Response({'error': 'No tienes suficientes futcoins para comprar este jugador.'},
                                status=status.HTTP_400_BAD_REQUEST)
            # Descontar los FutCoins del usuario
            usuario.futcoins -= costo_total
            usuario.save()

            # Crear la entrada de jugador_usuario
            jugador_usuario, created = JugadorUsuario.objects.get_or_create(usuario=usuario, jugador=jugador)
            if not created:
                jugador_usuario.cantidad += cantidad
                jugador_usuario.save()
            else:
                serializer.save(usuario=usuario, cantidad=cantidad)

            return Response({'success': 'Jugador comprado exitosamente.'}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PonerEnVentaUsuario(generics.CreateAPIView):
    serializer_class = VentaUsuarioSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        jugador_usuario = serializer.validated_data.get('jugador_usuario')
        precio = serializer.validated_data.get('precio')
        vendedor = self.request.user

        # Crear la entrada de venta
        serializer.save(vendedor=vendedor, jugador_usuario=jugador_usuario)


class MercadoUsuariosList(generics.ListAPIView):
    serializer_class = VentaUsuarioSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return VentaUsuario.objects.filter(isActive=True)


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

        # Transferir FutCoins
        comprador.futcoins -= venta.precio
        comprador.save()

        vendedor.futcoins += venta.precio
        vendedor.save()

        # Transferir la propiedad del jugador
        if jugador_usuario.cantidad < 1:
            return Response({'error': 'El jugador ya no está disponible.'}, status=status.HTTP_400_BAD_REQUEST)

        jugador_usuario.usuario = comprador
        jugador_usuario.save()

        # Marcar la venta como inactiva
        venta.isActive = False
        venta.save()

        return Response({'success': 'Jugador comprado exitosamente.'}, status=status.HTTP_200_OK)
