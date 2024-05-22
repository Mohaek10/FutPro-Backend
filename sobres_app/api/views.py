from random import random

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from cartas_app.models import Jugador
from sobres_app.models import Sobre, SobreJugador

# class ComprarSobreAPIView(APIView):
#     def post(self, request, *args, **kwargs):
#         sobre_id = request.data.get('sobre_id')
#         try:
#             sobre = Sobre.objects.get(id=sobre_id)
#         except Sobre.DoesNotExist:
#             return Response({'error': 'Sobre no encontrado'}, status=status.HTTP_404_NOT_FOUND)
#
#         # Generar jugadores aleatorios (suponiendo 5 jugadores por sobre)
#         jugadores_ids = list(Jugador.objects.values_list('id', flat=True))
#         jugadores_seleccionados = random.sample(jugadores_ids, 5)
#
#         for jugador_id in jugadores_seleccionados:
#             SobreJugador.objects.create(sobre=sobre, jugador_id=jugador_id)
#
#         return Response({'message': 'Sobre comprado exitosamente'}, status=status.HTTP_201_CREATED)
#
#
# class DescartarJugadorAPIView(APIView):
#     def post(self, request, *args, **kwargs):
#         sobre_jugador_id = request.data.get('sobre_jugador_id')
#         try:
#             sobre_jugador = SobreJugador.objects.get(id=sobre_jugador_id)
#             sobre_jugador.delete()
#             return Response({'message': 'Jugador descartado exitosamente'}, status=status.HTTP_204_NO_CONTENT)
#         except SobreJugador.DoesNotExist:
#             return Response({'error': 'Jugador no encontrado en el sobre'}, status=status.HTTP_404_NOT_FOUND)
