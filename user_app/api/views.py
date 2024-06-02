from venv import logger

from django.contrib import auth
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
# from user_app import models
from rest_framework.authtoken.models import Token
from user_app.api.serializers import RegistrationSerializer
from rest_framework_simplejwt.tokens import RefreshToken

from user_app.models import Account


@api_view(['POST'])
def login_view(request):
    data = {}
    if request.method == 'POST':
        email = request.data.get('email')
        password = request.data.get('password')

        # Validate input
        if not email or not password:
            data['response'] = 'Error de autenticación'
            data['error_message'] = 'Correo y contraseña son requeridos'
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

        account = auth.authenticate(email=email, password=password)

        if account is not None:
            data['response'] = 'Login exitoso'
            data['email'] = account.email
            data['username'] = account.username
            data['first_name'] = account.first_name
            data['last_name'] = account.last_name
            data['phone_number'] = account.phone_number
            data['futcoins'] = account.futcoins
            refresh = RefreshToken.for_user(account)
            data['token'] = {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
            return Response(data, status=status.HTTP_200_OK)
        else:
            data['response'] = 'Error de autenticación'
            data['error_message'] = 'Credenciales incorrectas'
            return Response(data, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def logout_view(request):
    data = {}
    try:
        refresh_token = request.data['refresh']
        token = RefreshToken(refresh_token)
        token.blacklist()
        data['response'] = 'Sesion cerrada'
        return Response(data, status=status.HTTP_200_OK)
    except Exception as e:
        # Log the exception
        logger.error(e)
        data['response'] = ('Token invalido, o no se ha proporcionado el token de refresco, por favor inicie sesion '
                            'nuevamente')
        return Response(data, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def register(request):
    if request.method == 'POST':
        serializer = RegistrationSerializer(data=request.data)
        data = {}
        if serializer.is_valid():
            account = serializer.save()
            data['response'] = 'El registro del usuario fue exitoso'
            data['username'] = account.username
            data['email'] = account.email
            data['first_name'] = account.first_name
            data['last_name'] = account.last_name
            data['phone_number'] = account.phone_number
            data['futcoins'] = account.futcoins
            refresh = RefreshToken.for_user(account)
            data['token'] = {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
            return Response(data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
