from venv import logger

from rest_framework import status, viewsets, generics
from rest_framework.exceptions import PermissionDenied, ValidationError, NotFound
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny, IsAuthenticatedOrReadOnly
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

from cartas_app.api.filters import JugadorFilter
from cartas_app.api.permissions import IsAdminorReadOnly, IsComentarioUserOrReadOnly
from cartas_app.api.serializers import JugadorSerializer, EquipoSerializer, ComentarioSerializer, \
    JugadorUsuarioSerializer
from cartas_app.models import Jugador, Equipo, Comentario, JugadorUsuario
from user_app.models import Account


class JugadorAV(viewsets.ModelViewSet):
    permission_classes = [IsAdminorReadOnly]
    serializer_class = JugadorSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = JugadorFilter
    search_fields = ['nombreCompleto', 'equipo__nombre']
    ordering_fields = ['media', 'edad', 'valor', 'createdAt']
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        if self.request.user.is_authenticated and self.request.user.is_admin:
            jugadores = Jugador.objects.all()
        else:
            jugadores = Jugador.activos()  # Los No-admins solo pueden ver
            # jugadores activos, osea los usuarios normales y los no autenticados
        return jugadores

    def create(self, request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_admin:
            return Response({'error': 'No tienes permiso para realizar esta acción.'}, status=status.HTTP_403_FORBIDDEN)

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_admin:
            return Response({'error': 'No tienes permiso para realizar esta acción.'}, status=status.HTTP_403_FORBIDDEN)
        logger.info(f'User {request.user} deleted player {kwargs["pk"]}')
        jugador = self.get_object()
        jugador.isActive = False
        jugador.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class JugadorDV(APIView):
    permission_classes = [IsAdminorReadOnly]

    def get_object(self, pk):
        return get_object_or_404(Jugador, pk=pk)

    def get(self, request, pk):
        jugador = self.get_object(pk)
        if not jugador.isActive and not request.user.is_admin:
            raise NotFound(detail="No Jugador matches the given query.")  # Forzar la misma excepción
        serializer = JugadorSerializer(jugador, context={'request': request})
        return Response(serializer.data)

    def put(self, request, pk):
        if not request.user.is_authenticated or not request.user.is_admin:
            return Response({'error': 'No tienes permiso para realizar esta acción.'}, status=status.HTTP_403_FORBIDDEN)
        logger.info(f'User {request.user} updated player {pk}')
        jugador = self.get_object(pk)
        serializer = JugadorSerializer(jugador, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_admin:
            return Response({'error': 'No tienes permiso para realizar esta acción.'}, status=status.HTTP_403_FORBIDDEN)
        logger.info(f'User {request.user} deleted player {kwargs["pk"]}')
        jugador = self.get_object(kwargs['pk'])
        jugador.isActive = False
        jugador.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class EquipoAV(viewsets.ModelViewSet):
    permission_classes = [IsAdminorReadOnly]
    serializer_class = EquipoSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['nombre']

    def get_queryset(self):
        if self.request.user.is_authenticated and self.request.user.is_admin:
            return Equipo.objects.all()  # Admins pueden ver todos los equipos
        return Equipo.activos()  # No-admins pueden ver solo los equipos activos

    def destroy(self, request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_admin:
            return Response({'error': 'No tienes permiso para realizar esta acción.'}, status=status.HTTP_403_FORBIDDEN)

        equipo = self.get_object()
        equipo.isActive = False
        equipo.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ComentarioList(generics.ListCreateAPIView):
    serializer_class = ComentarioSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        pk = self.kwargs['pk']
        return Comentario.objects.filter(jugador_id=pk)


class ComentarioDetalle(generics.RetrieveUpdateDestroyAPIView):
    queryset = Comentario.objects.all()
    serializer_class = ComentarioSerializer
    permission_classes = [IsComentarioUserOrReadOnly]


class ComentarioCreate(generics.CreateAPIView):
    serializer_class = ComentarioSerializer

    def perform_create(self, serializer):
        if not self.request.user.is_authenticated:
            raise PermissionDenied('Debes estar logueado para comentar')
        pk = self.kwargs.get('pk')
        jugador = get_object_or_404(Jugador, pk=pk)

        user = self.request.user
        comentario_queryset = Comentario.objects.filter(jugador=jugador, comentario_user=user)
        if comentario_queryset.exists():
            raise ValidationError({'error': 'Ya has comentado en este jugador.'})

        serializer.save(comentario_user=user, jugador=jugador)


class JugadorUsuarioView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, username):
        usuario = get_object_or_404(Account, username=username)
        jugador_usuario = JugadorUsuario.objects.filter(usuario=usuario)
        serializer = JugadorUsuarioSerializer(jugador_usuario, many=True)
        return Response(serializer.data)
