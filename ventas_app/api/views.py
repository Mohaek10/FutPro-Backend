from django.shortcuts import get_object_or_404
from rest_framework import status, generics
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework.views import APIView

from cartas_app.models import Jugador, JugadorUsuario
from ventas_app.api.serializers import MercadoSistemaSerializer, CompraSistemaSerializer, VentaUsuarioSerializer, \
    TransaccionSerializer
from ventas_app.models import VentaUsuario, Transaccion


# Vista para ver los jugadores en el mercado del sistema, que tienen en_mercado_sistema=True
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
                return Response({
                    'error': 'No tienes suficientes FutCoins para comprar este jugador.',
                    'futcoins': usuario.futcoins,
                    'precioTotal': costo_total
                }, status=status.HTTP_400_BAD_REQUEST)

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

            # Registrar la transacción
            Transaccion.objects.create(
                comprador=usuario,
                vendedor=None,
                jugador=jugador,
                precio=costo_total
            )

            data = {
                'success': 'Jugador comprado exitosamente.',
                'futcoins': usuario.futcoins,
                'jugador': jugador.nombreCompleto,
                'precioTotal': costo_total
            }
            return Response(data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MercadoUsuariosList(generics.ListAPIView):
    serializer_class = VentaUsuarioSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return VentaUsuario.objects.filter(isActive=True)


from django.db.models import Sum


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

        # Verificar la cantidad de jugadores a vender y las que tienes en jugador_usuario
        cantidad = serializer.validated_data.get('cantidad')
        if cantidad < 1:
            raise ValidationError({'error': 'La cantidad debe ser mayor a 0.'})

        # Verificar que el vendedor no está poniendo en venta más jugadores de los que posee
        total_en_venta = VentaUsuario.objects.filter(vendedor=vendedor, jugador_usuario=jugador_usuario,
                                                     isActive=True).aggregate(total=Sum('cantidad'))['total'] or 0
        if total_en_venta + cantidad > jugador_usuario.cantidad:
            raise ValidationError({'error': 'No puedes poner en venta más jugadores de los que posees.'})

        # Crear la entrada de venta
        serializer.save(vendedor=vendedor, jugador_usuario=jugador_usuario)


class ComprarJugadorUsuario(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, venta_id):
        venta = get_object_or_404(VentaUsuario, id=venta_id, isActive=True)
        comprador = self.request.user
        cantidad_a_comprar = request.data.get('cantidad', 1)

        if cantidad_a_comprar < 1:
            return Response({'error': 'La cantidad debe ser mayor a 0.'}, status=status.HTTP_400_BAD_REQUEST)
        if cantidad_a_comprar > venta.cantidad:
            return Response({'error': 'No puedes comprar más jugadores de los que están en venta.'},
                            status=status.HTTP_400_BAD_REQUEST)

        # Verificar que el comprador no sea el vendedor
        if venta.vendedor == comprador:
            return Response({'error': 'No puedes comprar tu propio jugador.'}, status=status.HTTP_400_BAD_REQUEST)
        costo_total = venta.precio * cantidad_a_comprar

        if comprador.futcoins < costo_total:
            return Response({'error': 'No tienes suficientes FutCoins para comprar este jugador.'},
                            status=status.HTTP_400_BAD_REQUEST)

        vendedor = venta.vendedor
        jugador_usuario = venta.jugador_usuario

        # Verificar si el vendedor aun tiene el jugador
        if not JugadorUsuario.objects.filter(usuario=vendedor, jugador=jugador_usuario.jugador).exists():
            return Response({'error': 'El jugador ya no está disponible.'}, status=status.HTTP_400_BAD_REQUEST)

        # Verificar que el jugador está disponible
        if jugador_usuario.cantidad < cantidad_a_comprar:
            return Response({'error': 'El jugador ya no está disponible.'}, status=status.HTTP_400_BAD_REQUEST)

        # Transferir FutCoins
        comprador.futcoins -= costo_total
        comprador.save()

        vendedor.futcoins += costo_total
        vendedor.save()

        # Actualizar la cantidad del jugador en el vendedor
        jugador_usuario.cantidad -= cantidad_a_comprar
        if jugador_usuario.cantidad == 0:
            jugador_usuario.delete()
            jugador_usuario.save()
        else:
            jugador_usuario.save()

        # Crear o actualizar la entrada del comprador en JugadorUsuario
        jugador_comprador, created = JugadorUsuario.objects.get_or_create(
            usuario=comprador,
            jugador=jugador_usuario.jugador
        )
        if created:
            jugador_comprador.cantidad = cantidad_a_comprar
        else:
            jugador_comprador.cantidad += cantidad_a_comprar
        jugador_comprador.save()

        # Marcar la venta como inactiva si todas las cartas han sido vendidas
        if venta.cantidad == cantidad_a_comprar:
            venta.isActive = False
        else:
            venta.cantidad -= cantidad_a_comprar
        venta.save()

        # Registrar la transacción
        Transaccion.objects.create(
            comprador=comprador,
            vendedor=vendedor,
            jugador=jugador_usuario.jugador,
            cantidad=cantidad_a_comprar,
            precio=costo_total
        )
        data = {
            'success': 'Jugador comprado exitosamente.',
            'jugador': jugador_usuario.jugador.nombreCompleto,
            'precioTotal': costo_total,
            'futcoins': comprador.futcoins
        }

        return Response(data, status=status.HTTP_200_OK)


class EliminarJugadorDelMercado(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, venta_id):
        venta = get_object_or_404(VentaUsuario, id=venta_id, isActive=True)
        vendedor = self.request.user

        # Verificar que el vendedor es el dueño de la venta
        if venta.vendedor != vendedor:
            return Response({'error': 'No tienes permiso para eliminar esta venta.'},
                            status=status.HTTP_403_FORBIDDEN)

        # Marcar la venta como inactiva
        venta.isActive = False
        venta.save()

        return Response({'success': 'Venta eliminada exitosamente.'}, status=status.HTTP_200_OK)


class TransaccionesUsuarioList(generics.ListAPIView):
    serializer_class = TransaccionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Transaccion.objects.filter(comprador=self.request.user) | Transaccion.objects.filter(
            vendedor=self.request.user)


class TransaccionesAdminList(generics.ListAPIView):
    serializer_class = TransaccionSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        return Transaccion.objects.all()
