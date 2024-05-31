from rest_framework import status, viewsets, generics
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny, IsAuthenticatedOrReadOnly
from django.shortcuts import get_object_or_404

from cartas_app.api.permissions import IsAdminorReadOnly, IsComentarioUserOrReadOnly
from cartas_app.api.serializers import JugadorSerializer, EquipoSerializer, ComentarioSerializer
from cartas_app.models import Jugador, Equipo, Comentario


class JugadorAV(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        if request.user.is_staff:
            jugadores = Jugador.objects.all()  # Admins can see all players
        else:
            jugadores = Jugador.activos()  # Non-admins can see only active players
        serializer = JugadorSerializer(jugadores, many=True)
        return Response(serializer.data)

    def post(self, request):
        if not request.user.is_authenticated or not request.user.is_staff:
            return Response({'error': 'No tienes permiso para realizar esta acción.'}, status=status.HTTP_403_FORBIDDEN)

        serializer = JugadorSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class JugadorDV(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_object(self, pk):
        return get_object_or_404(Jugador, pk=pk)

    def get(self, request, pk):
        jugador = self.get_object(pk)
        if not jugador.isActive and not request.user.is_staff:
            return Response({'error': 'Jugador no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        serializer = JugadorSerializer(jugador)
        return Response(serializer.data)

    def put(self, request, pk):
        if not request.user.is_authenticated or not request.user.is_staff:
            return Response({'error': 'No tienes permiso para realizar esta acción.'}, status=status.HTTP_403_FORBIDDEN)

        jugador = self.get_object(pk)
        serializer = JugadorSerializer(jugador, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        if not request.user.is_authenticated or not request.user.is_staff:
            return Response({'error': 'No tienes permiso para realizar esta acción.'}, status=status.HTTP_403_FORBIDDEN)

        jugador = self.get_object(pk)
        jugador.isActive = False
        jugador.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class EquipoAV(viewsets.ModelViewSet):
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        if self.request.user.is_authenticated and self.request.user.is_staff:
            return Equipo.objects.all()  # Admins can see all teams
        return Equipo.activos()  # Non-admins can see only active teams

    serializer_class = EquipoSerializer

    def destroy(self, request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_staff:
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
            raise ValidationError('Ya has comentado este jugador')

        serializer.save(comentario_user=user, jugador=jugador)
