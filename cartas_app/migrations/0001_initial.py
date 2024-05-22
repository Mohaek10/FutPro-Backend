# Generated by Django 5.0.6 on 2024-05-22 11:42

import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Equipo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=250)),
                ('liga', models.CharField(max_length=250)),
                ('pais', models.CharField(max_length=150)),
                ('escudo', models.CharField(max_length=500)),
                ('createdAt', models.DateTimeField(auto_now_add=True)),
                ('updatedAt', models.DateTimeField(auto_now=True)),
                ('isActive', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='Jugador',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombreCompleto', models.CharField(max_length=250)),
                ('edad', models.IntegerField()),
                ('media', models.IntegerField()),
                ('rareza', models.CharField(max_length=250)),
                ('imagen', models.ImageField(upload_to='jugadores/')),
                ('valor', models.DecimalField(decimal_places=2, max_digits=10)),
                ('posicion', models.CharField(choices=[('DC', 'Delantero Centro'), ('EI', 'Extremo Izquierdo'), ('ED', 'Extremo Derecho'), ('SD', 'Segundo Delantero'), ('MCO', 'Mediapunta'), ('CDM', 'Mediocentro Defensivo'), ('CM', 'Mediocentro'), ('DFC', 'Defensa Central'), ('LD', 'Lateral Derecho'), ('LI', 'Lateral Izquierdo'), ('CAD', 'Carrilero Derecho'), ('CAI', 'Carrilero Izquierdo'), ('PT', 'Portero')], max_length=3)),
                ('createdAt', models.DateTimeField(auto_now_add=True)),
                ('updatedAt', models.DateTimeField(auto_now=True)),
                ('isActive', models.BooleanField(default=True)),
                ('equipo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='jugadores', to='cartas_app.equipo')),
            ],
        ),
        migrations.CreateModel(
            name='Comentario',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('calificacion', models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)])),
                ('texto', models.CharField(max_length=200)),
                ('createdAt', models.DateTimeField(auto_now_add=True)),
                ('updatedAt', models.DateTimeField(auto_now=True)),
                ('isActive', models.BooleanField(default=True)),
                ('comentario_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('jugador', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comentarios', to='cartas_app.jugador')),
            ],
        ),
    ]
