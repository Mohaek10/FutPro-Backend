from rest_framework import serializers
from django.contrib.auth.models import User

from user_app.models import Account


# Clase para serializar el modelo de usuario de Django, que comprueba que el password y el password2 sean iguales,
# y que el email no este ya registrado
class RegistrationSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(style={'input_type': 'password'}, write_only=True)

    class Meta:
        model = Account
        fields = ['username', 'email', 'password', 'password2', 'first_name', 'last_name', 'phone_number']
        extra_kwargs = {
            'password': {'write_only': True}
        }

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
