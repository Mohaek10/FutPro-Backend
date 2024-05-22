from django.contrib import admin

from cartas_app.models import Jugador, Equipo, Comentario

# Register your models here.
admin.site.register(Jugador)
admin.site.register(Equipo)
admin.site.register(Comentario)
