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

    def validate_edad(self, value):
        if value < 0 or value > 100:
            raise serializers.ValidationError("La edad debe estar entre 0 y 100 años.")
        return value

    def validate_media(self, value):
        if value < 0 or value > 100:
            raise serializers.ValidationError("La media debe estar entre 0 y 100.")
        return value

    def validate_posicion(self, value):
        valid_positions = [choice[0] for choice in Jugador.POSICION_CHOICES]
        if value not in valid_positions:
            raise serializers.ValidationError(
                f"La posición debe ser una de las siguientes: {', '.join(valid_positions)}.")
        return value

    def validate_rareza(self, value):
        valid_rareza = ['Común', 'Rara', 'Épica', 'Legendaria']
        if value not in valid_rareza:
            raise serializers.ValidationError(f"La rareza debe ser una de las siguientes: {', '.join(valid_rareza)}.")
        return value

    def validate_valor(self, value):
        if value < 0:
            raise serializers.ValidationError("El valor no puede ser negativo.")
        return value


class EquipoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Equipo
        fields = '__all__'

    jugadores = JugadorSerializer(many=True, read_only=True)
