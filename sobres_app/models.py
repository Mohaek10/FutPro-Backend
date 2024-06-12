from django.db import models

from cartas_app.models import Jugador


# Create your models here.
class Sobre(models.Model):
    TIPO_CHOICES = [
        ('Básico', 'Básico'),
        ('Especial', 'Especial'),
        ('Premium', 'Premium'),
        ('Platino', 'Platino'),
    ]

    nombre = models.CharField(max_length=250)
    tipo = models.CharField(max_length=50, choices=TIPO_CHOICES)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    imagen = models.ImageField(upload_to='sobres/', null=True, blank=True)
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)
    isActive = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre


class SobreJugador(models.Model):
    sobre = models.ForeignKey(Sobre, on_delete=models.CASCADE, related_name='sobre_jugadores')
    jugador = models.ForeignKey(Jugador, on_delete=models.CASCADE)
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)
    isActive = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.sobre.nombre} - {self.jugador.nombreCompleto}"
