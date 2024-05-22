from rest_framework import status, viewsets, generics
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from cartas_app.api.permissions import IsAdminorReadOnly, IsComentarioUserOrReadOnly
from cartas_app.api.serializers import JugadorSerializer, EquipoSerializer, ComentarioSerializer
from cartas_app.models import Jugador, Equipo, Comentario


class JugadorAV(APIView):
    def get(self, request):
        jugador = Jugador.objects.all()
        serializer = JugadorSerializer(jugador, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = JugadorSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class JugadorDV(APIView):
    def get(self, request, pk):
        jugador = Jugador.objects.filter(id=pk).first()
        if jugador:
            serializer = JugadorSerializer(jugador)
            return Response(serializer.data)
        return Response({'error': 'Jugador no encontrado'}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, pk):
        jugador = Jugador.objects.filter(id=pk).first()
        if jugador:
            serializer = JugadorSerializer(jugador, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({'error': 'Jugador no encontrado'}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, pk):
        jugador = Jugador.objects.filter(id=pk).first()
        if jugador:
            jugador.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({'error': 'Jugador no encontrado'}, status=status.HTTP_404_NOT_FOUND)


class EquipoAV(viewsets.ModelViewSet):
    permission_classes = [IsAdminorReadOnly]
    queryset = Equipo.objects.all()
    serializer_class = EquipoSerializer


class ComentarioList(generics.ListCreateAPIView):
    serialize_class = ComentarioSerializer
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
