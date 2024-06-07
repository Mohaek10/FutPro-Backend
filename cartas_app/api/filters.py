from django_filters import rest_framework as filters

from cartas_app.models import Jugador


class JugadorFilter(filters.FilterSet):
    nombreCompleto = filters.CharFilter(field_name='nombreCompleto', lookup_expr='icontains')
    media = filters.RangeFilter(field_name='media')
    equipo = filters.CharFilter(field_name='equipo__nombre', lookup_expr='icontains')
    rareza = filters.CharFilter(field_name='rareza', lookup_expr='exact')
    posicion = filters.CharFilter(field_name='posicion', lookup_expr='exact')

    class Meta:
        model = Jugador
        fields = ['nombreCompleto', 'media', 'equipo', 'rareza', 'posicion']
