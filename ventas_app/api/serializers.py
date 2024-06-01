from rest_framework import serializers
from cartas_app.models import JugadorUsuario
from ventas_app.models import Venta


class CompraSerializer(serializers.ModelSerializer):
    class Meta:
        model = JugadorUsuario
        fields = ['jugador', 'cantidad']


class VentaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Venta
        fields = ['jugador_usuario', 'precio']
