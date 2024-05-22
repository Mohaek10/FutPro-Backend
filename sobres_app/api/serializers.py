from rest_framework import serializers
from cartas_app.models import Jugador
from sobres_app.models import Sobre, SobreJugador


class SobreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sobre
        fields = '__all__'


class SobreJugadorSerializer(serializers.ModelSerializer):
    jugador = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = SobreJugador
        fields = '__all__'
