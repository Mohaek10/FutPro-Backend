# Generated by Django 5.0.6 on 2024-06-03 11:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ventas_app', '0002_ventausuario_cantidad'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaccion',
            name='cantidad',
            field=models.PositiveIntegerField(default=1),
        ),
    ]
