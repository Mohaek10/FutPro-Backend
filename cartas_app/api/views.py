from rest_framework.views import APIView

from cartas_app.models import Jugador


class JugadorAV(APIView):
    def get(self, request):
        jugador = Jugador.objects.all()
