from venv import logger

from django.contrib import auth
from rest_framework import status, generics
from rest_framework.decorators import api_view
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
# from user_app import models
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView

from cartas_app.api.serializers import JugadorUsuarioSerializer
from cartas_app.models import JugadorUsuario
from user_app.api.serializers import RegistrationSerializer, CompraFutCoinsSerializer, LoteFutCoinsSerializer
from rest_framework_simplejwt.tokens import RefreshToken

from user_app.models import Account, CompraFutCoins, LoteFutCoins


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


# Ver mis jugadores
class JugadoresUsuarioList(generics.ListAPIView):
    serializer_class = JugadorUsuarioSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return JugadorUsuario.objects.filter(usuario=self.request.user)


class LotesFutCoinsList(generics.ListAPIView):
    serializer_class = LoteFutCoinsSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return LoteFutCoins.objects.all()


class ComprarFutCoins(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = CompraFutCoinsSerializer(data=request.data)
        if serializer.is_valid():
            lote_id = serializer.validated_data.get('lote').id
            numero_tarjeta = serializer.validated_data.get('numero_tarjeta')
            fecha_expiracion = serializer.validated_data.get('fecha_expiracion')
            cvv = serializer.validated_data.get('cvv')

            # Aquí puedes agregar la lógica para procesar el pago con el número de tarjeta
            # Por simplicidad, asumimos que el pago es exitoso

            usuario = request.user
            lote = get_object_or_404(LoteFutCoins, id=lote_id)

            # Incrementar FutCoins del usuario
            usuario.futcoins += lote.cantidad
            usuario.save()

            # Registrar la compra de FutCoins
            CompraFutCoins.objects.create(
                usuario=usuario,
                lote=lote,
                numero_tarjeta=numero_tarjeta,
                fecha_expiracion=fecha_expiracion,
                cvv=cvv
            )

            data = {
                'success': 'FutCoins compradas exitosamente.',
                'futcoins': usuario.futcoins,
                'lote': lote.nombre,
                'cantidad': lote.cantidad,
                'precio': lote.precio
            }
            return Response(data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
