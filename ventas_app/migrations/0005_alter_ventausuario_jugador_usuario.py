# Generated by Django 5.0.6 on 2024-06-03 13:15

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cartas_app', '0001_initial'),
        ('ventas_app', '0004_alter_ventausuario_jugador_usuario'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ventausuario',
            name='jugador_usuario',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cartas_app.jugadorusuario'),
        ),
    ]
