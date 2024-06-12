from django.contrib import admin

# Register your models here.
from sobres_app.models import Sobre, SobreJugador

admin.site.register(Sobre)
admin.site.register(SobreJugador)
