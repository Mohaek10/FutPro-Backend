from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from user_app.models import Account


# Create your models here.

class Equipo(models.Model):
    nombre = models.CharField(max_length=250)
    liga = models.CharField(max_length=250)
    pais = models.CharField(max_length=150)
    escudo = models.CharField(max_length=500)
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)
    isActive = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre

    @staticmethod
    def activos():
        return Equipo.objects.filter(isActive=True)


class Jugador(models.Model):
    POSICION_CHOICES = [
        ('DC', 'Delantero Centro'),
        ('EI', 'Extremo Izquierdo'),
        ('ED', 'Extremo Derecho'),
        ('SD', 'Segundo Delantero'),
        ('MCO', 'Mediapunta'),
        ('CDM', 'Mediocentro Defensivo'),
        ('CM', 'Mediocentro'),
        ('DFC', 'Defensa Central'),
        ('LD', 'Lateral Derecho'),
        ('LI', 'Lateral Izquierdo'),
        ('CAD', 'Carrilero Derecho'),
        ('CAI', 'Carrilero Izquierdo'),
        ('PT', 'Portero'),
    ]
    RAREZA_CHOICES = [
        ('Común', 'Común'),
        ('Rara', 'Rara'),
        ('Épica', 'Épica'),
        ('Legendaria', 'Legendaria'),
    ]  # Rareza de las cartas
    nombreCompleto = models.CharField(max_length=250)
    edad = models.IntegerField()
    equipo = models.ForeignKey(Equipo, on_delete=models.CASCADE, related_name='jugadores')
    media = models.IntegerField()
    rareza = models.CharField(max_length=250)
    imagen = models.ImageField(upload_to='jugadores/', null=True, blank=True)
    valor = models.DecimalField(max_digits=13, decimal_places=2)
    posicion = models.CharField(max_length=3, choices=POSICION_CHOICES)
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)
    en_mercado = models.BooleanField(default=True)
    isActive = models.BooleanField(default=True)

    def __str__(self):
        return self.nombreCompleto

    @staticmethod
    def activos():
        return Jugador.objects.filter(isActive=True)

    def clean(self):
        if self.media < 0 or self.media > 100:
            raise ValidationError('La media debe estar entre 0 y 100')
        if self.edad < 0 or self.edad > 100:
            raise ValidationError('La edad debe estar entre 0 y 100')
        if self.valor < 0:
            raise ValidationError('El valor no puede ser negativo')
        if self.posicion not in dict(self.POSICION_CHOICES).keys():
            raise ValidationError('Posición no válida')
        if self.rareza not in ['Común', 'Rara', 'Épica', 'Legendaria']:
            raise ValidationError('Rareza no válida')

    def save(self, *args, **kwargs):
        self.full_clean()
        super(Jugador, self).save(*args, **kwargs)


class Comentario(models.Model):
    comentario_user = models.ForeignKey(Account, on_delete=models.CASCADE)
    calificacion = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    texto = models.CharField(max_length=200)
    jugador = models.ForeignKey(Jugador, on_delete=models.CASCADE, related_name='comentarios')
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)
    isActive = models.BooleanField(default=True)

    def __str__(self):
        return str(self.calificacion) + " - " + self.jugador.nombreCompleto


# Modelo intermedio para la relación muchos a muchos entre Jugador y Account
class JugadorUsuario(models.Model):
    usuario = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='jugadores')
    jugador = models.ForeignKey(Jugador, on_delete=models.CASCADE, related_name='usuarios')
    cantidad = models.PositiveIntegerField(default=1)
    fecha_adquisicion = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('usuario', 'jugador')

    def __str__(self):
        return f"{self.usuario.username} posee {self.cantidad} de {self.jugador.nombreCompleto}"
