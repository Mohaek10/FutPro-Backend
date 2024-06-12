from rest_framework import serializers

from cartas_app.api.serializers import JugadorSerializer
from cartas_app.models import Jugador
from ventas_app.models import VentaUsuario, Transaccion


class MercadoSistemaSerializer(serializers.ModelSerializer):
    nombre_equipo = serializers.SerializerMethodField()
    escudo = serializers.SerializerMethodField()

    class Meta:
        model = Jugador
        fields = ['id', 'nombreCompleto', 'edad', 'media', 'rareza', 'imagen', 'valor', 'posicion', 'en_mercado',
                  'nombre_equipo', 'updatedAt', 'escudo']

    def get_nombre_equipo(self, obj):
        return obj.equipo.nombre

    def get_escudo(self, obj):
        return obj.equipo.escudo


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


class VentaUsuarioSerializer(serializers.ModelSerializer):
    vendedor = serializers.ReadOnlyField(source='vendedor.username')
    jugador_id = serializers.SerializerMethodField()
    # jugador_nombre = serializers.ReadOnlyField(source='jugador_usuario.jugador.nombreCompleto')
    jugador = JugadorSerializer(read_only=True, source='jugador_usuario.jugador')

    class Meta:
        model = VentaUsuario
        fields = '__all__'

    def get_jugador_id(self, obj):
        return obj.jugador_usuario.jugador.id

    def validate_jugador_usuario(self, value):
        request = self.context.get('request')
        if value.usuario != request.user:
            raise serializers.ValidationError("No puedes vender un jugador que no posees.")
        return value


class TransaccionSerializer(serializers.ModelSerializer):
    comprador_username = serializers.SerializerMethodField()
    vendedor_username = serializers.SerializerMethodField()
    jugador_nombre = serializers.SerializerMethodField()

    class Meta:
        model = Transaccion
        fields = ['id', 'comprador_username', 'vendedor_username', 'jugador_nombre', 'cantidad', 'precio', 'fecha']

    def get_comprador_username(self, obj):
        return obj.comprador.username

    def get_vendedor_username(self, obj):
        return obj.vendedor.username if obj.vendedor else None

    def get_jugador_nombre(self, obj):
        return obj.jugador.nombreCompleto
