from django.db import models
from user_app.models import Account
from cartas_app.models import JugadorUsuario, Jugador


class VentaUsuario(models.Model):
    vendedor = models.ForeignKey(Account, related_name='ventas_hechas', on_delete=models.CASCADE)
    jugador_usuario = models.ForeignKey(JugadorUsuario, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    fecha = models.DateTimeField(auto_now_add=True)
    isActive = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.jugador_usuario.jugador.nombreCompleto} en venta por {self.precio} FutCoins"


class Transaccion(models.Model):
    comprador = models.ForeignKey(Account, related_name='compras', on_delete=models.CASCADE)
    vendedor = models.ForeignKey(Account, related_name='ventas', on_delete=models.CASCADE, null=True, blank=True)
    jugador = models.ForeignKey(Jugador, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.comprador.username} compró {self.jugador.nombreCompleto} por {self.precio} FutCoins"
