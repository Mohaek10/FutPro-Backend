# Generated by Django 5.0.6 on 2024-06-03 13:13

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cartas_app', '0001_initial'),
        ('ventas_app', '0003_transaccion_cantidad'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ventausuario',
            name='jugador_usuario',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='cartas_app.jugadorusuario'),
        ),
    ]