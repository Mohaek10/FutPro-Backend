from rest_framework import serializers
from cartas_app.models import JugadorUsuario, Jugador
from ventas_app.models import Venta


class CompraSerializer(serializers.ModelSerializer):
    class Meta:
        model = JugadorUsuario
        fields = ['jugador', 'cantidad']


class VentaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Venta
        fields = ['jugador_usuario', 'precio']


class MercadoSistemaSerializer(serializers.ModelSerializer):
    nombre_equipo = serializers.SerializerMethodField()

    class Meta:
        model = Jugador
        fields = ['id', 'nombreCompleto', 'edad', 'media', 'rareza', 'imagen', 'valor', 'posicion', 'en_mercado']

    def get_nombre_equipo(self, obj):
        return obj.equipo.nombre


class CompraSistemaSerializer(serializers.Serializer):
    jugador_id = serializers.IntegerField()
    cantidad = serializers.IntegerField()

    def validate_jugador_id(self, value):
        try:
            jugador = Jugador.objects.get(id=value)
        except Jugador.DoesNotExist:
            raise serializers.ValidationError("No existe un jugador con ese ID.")
        if not jugador.en_mercado:
            raise serializers.ValidationError("El jugador seleccionado no está en el mercado.")
        return value

    def validate_cantidad(self, value):
        if value < 1:
            raise serializers.ValidationError("La cantidad debe ser mayor a 0.")
        return value