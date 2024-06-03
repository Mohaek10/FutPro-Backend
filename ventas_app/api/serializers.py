from rest_framework import serializers
from cartas_app.models import Jugador
from ventas_app.models import VentaUsuario, Transaccion


class MercadoSistemaSerializer(serializers.ModelSerializer):
    nombre_equipo = serializers.SerializerMethodField()

    class Meta:
        model = Jugador
        fields = ['id', 'nombreCompleto', 'edad', 'media', 'rareza', 'imagen', 'valor', 'posicion', 'en_mercado',
                  'nombre_equipo', 'updatedAt']

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


class VentaUsuarioSerializer(serializers.ModelSerializer):
    vendedor = serializers.ReadOnlyField(source='vendedor.username')

    class Meta:
        model = VentaUsuario
        fields = ['id', 'vendedor', 'cantidad', 'jugador_usuario', 'precio', 'fecha', 'isActive']

    def validate_jugador_usuario(self, value):
        request = self.context.get('request')
        if value.usuario != request.user:
            raise serializers.ValidationError("No puedes vender un jugador que no posees.")
        return value


class TransaccionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaccion
        fields = ['id', 'comprador', 'vendedor', 'jugador', 'precio', 'fecha']
        depth = 1  # Optional: to include related fields details
