from rest_framework import serializers

from cartas_app.models import Jugador, Comentario, Equipo


class ComentarioSerializer(serializers.ModelSerializer):
    comentario_user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Comentario
        fields = '__all__'


class JugadorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Jugador
        fields = '__all__'


class EquipoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Equipo
        fields = '__all__'

    jugadores = JugadorSerializer(many=True, read_only=True)
