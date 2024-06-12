from venv import logger
from rest_framework import serializers
from django.contrib import auth
from django.contrib.auth.password_validation import validate_password
from rest_framework import status, generics, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.response import Response
# from user_app import models
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView

from user_app.api.permissions import IsAdminorReadOnly
from cartas_app.api.serializers import JugadorUsuarioSerializer
from cartas_app.models import JugadorUsuario
from user_app.api.serializers import RegistrationSerializer, CompraFutCoinsSerializer, LoteFutCoinsSerializer, \
    UserProfileSerializer, ChangePasswordSerializer
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
            data['date_joined'] = account.date_joined
            data['last_login'] = account.last_login
            data['is_admin'] = account.is_admin
            data['is_active'] = account.is_active
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
            data['date_joined'] = account.date_joined
            data['last_login'] = account.last_login
            data['is_admin'] = account.is_admin
            data['is_active'] = account.is_active
            refresh = RefreshToken.for_user(account)
            data['token'] = {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
            return Response(data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def check_admin_status(request):
    user = request.user
    print(user.is_admin)
    return Response({'is_admin': user.is_admin}, status=status.HTTP_200_OK)


class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            old_password = serializer.validated_data['old_password']
            new_password = serializer.validated_data['new_password']

            if not request.user.check_password(old_password):
                return Response({'old_password': 'La contraseña antigua no es correcta'},
                                status=status.HTTP_400_BAD_REQUEST)

            try:
                validate_password(new_password, request.user)
            except serializers.ValidationError as e:
                return Response({'new_password': e.messages}, status=status.HTTP_400_BAD_REQUEST)

            request.user.set_password(new_password)
            request.user.save()
            return Response({'success': 'La contraseña ha sido cambiada exitosamente'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Ver mis jugadores
class JugadoresUsuarioList(generics.ListAPIView):
    serializer_class = JugadorUsuarioSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return JugadorUsuario.objects.filter(usuario=self.request.user)


class LotesFutCoinsList(viewsets.ModelViewSet):
    permission_classes = [IsAdminorReadOnly]
    serializer_class = LoteFutCoinsSerializer
    queryset = LoteFutCoins.objects.all()


class ComprarFutCoins(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = CompraFutCoinsSerializer(data=request.data)
        if serializer.is_valid():
            lote_id = serializer.validated_data.get('lote').id
            numero_tarjeta = serializer.validated_data.get('numero_tarjeta')
            fecha_expiracion = serializer.validated_data.get('fecha_expiracion')
            cvv = serializer.validated_data.get('cvv')

            # Para simplificar mi api y no tener que hacer validaciones de tarjeta de credito, solo se incrementa
            # la cantidad de futcoins y se da por hecho que la compra fue exitosa, en una aplicacion real se deberia
            # validar la tarjeta de credito y añadir una pasarela de pago con el banco

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


class VerCompras(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        compras = CompraFutCoins.objects.filter(usuario=request.user)
        serializer = CompraFutCoinsSerializer(compras, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class VerTodasLasComprasAdmin(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        compras = CompraFutCoins.objects.all()
        serializer = CompraFutCoinsSerializer(compras, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
