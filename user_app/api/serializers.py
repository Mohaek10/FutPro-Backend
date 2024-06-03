from rest_framework import serializers
from django.contrib.auth.models import User

from user_app.models import Account, LoteFutCoins, CompraFutCoins


# Clase para serializar el modelo de usuario de Django, que comprueba que el password y el password2 sean iguales,
# y que el email no este ya registrado
class RegistrationSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(style={'input_type': 'password'}, write_only=True)

    class Meta:
        model = Account
        fields = ['username', 'email', 'password', 'password2', 'first_name', 'last_name', 'phone_number', 'futcoins']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def validate_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError('La contraseña debe tener al menos 8 caracteres')
        if not any(char.isdigit() for char in value):
            raise serializers.ValidationError('La contraseña debe tener al menos un número')
        return value

    def save(self):
        password = self.validated_data['password']
        password2 = self.validated_data['password2']

        if password != password2:
            raise serializers.ValidationError({'error': 'El password de confirmacion no coincide'})
        if Account.objects.filter(email=self.validated_data['email']).exists():
            raise serializers.ValidationError({'error': 'El email ya esta registrado'})
        account = Account.objects.create_user(
            first_name=self.validated_data['first_name'],
            last_name=self.validated_data['last_name'],
            username=self.validated_data['username'],
            email=self.validated_data['email'],
            password=self.validated_data['password']
        )
        account.phone_number = self.validated_data['phone_number']

        account.save()
        return account


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ['first_name', 'last_name', 'username', 'email', 'phone_number', 'futcoins']
        read_only_fields = ['futcoins']


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    def validate_new_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError('La contraseña debe tener al menos 8 caracteres')
        if not any(char.isdigit() for char in value):
            raise serializers.ValidationError('La contraseña debe tener al menos un número')
        return value


class LoteFutCoinsSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoteFutCoins
        fields = ['id', 'nombre', 'cantidad', 'precio']


class CompraFutCoinsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompraFutCoins
        fields = ['id', 'usuario', 'lote', 'numero_tarjeta', 'fecha_expiracion', 'cvv', 'fecha']
        extra_kwargs = {
            'usuario': {'read_only': True},
            'fecha': {'read_only': True}
        }

    def validate_numero_tarjeta(self, value):
        if len(value) != 16:
            raise serializers.ValidationError('El número de tarjeta debe tener 16 dígitos')
        return value

    def validate_fecha_expiracion(self, value):
        if len(value) != 5:
            raise serializers.ValidationError('La fecha de expiración debe tener el formato MM/YY')
        return value

    def validate_cvv(self, value):
        if not value.isdigit() or len(value) != 3:
            raise serializers.ValidationError('El CVV debe tener 3 dígitos')
        return value
