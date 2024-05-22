from django.db import models


# Create your models here.

class Equipo(models.Model):
    nombre = models.CharField(max_length=250)
    liga = models.CharField(max_length=250)
    pais = models.CharField(max_length=150)
    escudo = models.CharField(max_length=500)
    isActive = models.BooleanField(default=True)
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nombre
