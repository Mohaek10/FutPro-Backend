from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from cartas_app.api.serializers import JugadorSerializer, EquipoSerializer
from cartas_app.models import Jugador, Equipo


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
    queryset = Equipo.objects.all()
    serializer_class = EquipoSerializer
