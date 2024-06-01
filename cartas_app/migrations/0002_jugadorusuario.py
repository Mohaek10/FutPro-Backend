# Generated by Django 5.0.6 on 2024-05-31 17:45

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cartas_app', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='JugadorUsuario',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cantidad', models.PositiveIntegerField(default=1)),
                ('fecha_adquisicion', models.DateTimeField(auto_now_add=True)),
                ('jugador', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='usuarios', to='cartas_app.jugador')),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='jugadores', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('usuario', 'jugador')},
            },
        ),
    ]