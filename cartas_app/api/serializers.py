import logging

from rest_framework import serializers

from cartas_app.models import Jugador, Comentario, Equipo, JugadorUsuario
from user_app.models import Account

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)


class ComentarioSerializer(serializers.ModelSerializer):
    comentario_user = serializers.SerializerMethodField()

    class Meta:
        model = Comentario
        fields = '__all__'

    @staticmethod
    def get_comentario_user(obj):
        return obj.comentario_user.username


class JugadorSerializer(serializers.ModelSerializer):
    comentarios = ComentarioSerializer(many=True, read_only=True)
    nombre_equipo = serializers.SerializerMethodField()

    class Meta:
        model = Jugador
        fields = '__all__'
        read_only_fields = ['createdAt', 'updatedAt', 'en_mercado', 'isActive', ]

    def get_nombre_equipo(self, obj):
        return obj.equipo.nombre

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

    def create(self, validated_data):
        validated_data['isActive'] = True
        
        return super(JugadorSerializer, self).create(validated_data)


class EquipoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Equipo
        fields = '__all__'

    def to_representation(self, instance):
        request = self.context.get('request')
        if not instance.isActive and (not request or not request.user.is_admin):
            return None
        return super(EquipoSerializer, self).to_representation(instance)

    jugadores = JugadorSerializer(many=True, read_only=True)


class JugadorUsuarioSerializer(serializers.ModelSerializer):
    usuario = serializers.PrimaryKeyRelatedField(queryset=Account.objects.all())
    username = serializers.SerializerMethodField()
    jugador = serializers.PrimaryKeyRelatedField(queryset=Jugador.objects.all())
    nombreCompleto = serializers.SerializerMethodField()

    class Meta:
        model = JugadorUsuario
        fields = '__all__'

    def get_username(self, obj):
        return obj.usuario.username

    def get_nombreCompleto(self, obj):
        return obj.jugador.nombreCompleto
