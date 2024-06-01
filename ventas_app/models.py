from django.db import models
from user_app.models import Account
from cartas_app.models import JugadorUsuario


class VentaUsuario(models.Model):
    vendedor = models.ForeignKey(Account, related_name='ventas_hechas', on_delete=models.CASCADE)
    jugador_usuario = models.ForeignKey(JugadorUsuario, on_delete=models.CASCADE)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    fecha = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.jugador_usuario.jugador.nombreCompleto} en venta por {self.precio} FutCoins"
