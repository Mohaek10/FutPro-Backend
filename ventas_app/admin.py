from django.contrib import admin

from ventas_app.models import VentaUsuario, Transaccion

# Register your models here.
admin.site.register(VentaUsuario)
admin.site.register(Transaccion)
