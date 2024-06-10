from django_filters import rest_framework as filters

from ventas_app.models import VentaUsuario


class VentaUsuarioFilter(filters.FilterSet):
    nombreCompleto = filters.CharFilter(field_name='jugador_usuario__jugador__nombreCompleto', lookup_expr='icontains')
    media = filters.RangeFilter(field_name='jugador_usuario__jugador__media')
    valor = filters.RangeFilter(field_name='precio')
    equipo = filters.CharFilter(field_name='jugador_usuario__jugador__equipo__nombre', lookup_expr='icontains')
    rareza = filters.CharFilter(field_name='jugador_usuario__jugador__rareza', lookup_expr='exact')
    posicion = filters.CharFilter(field_name='jugador_usuario__jugador__posicion', lookup_expr='exact')

    class Meta:
        model = VentaUsuario
        fields = ['nombreCompleto', 'media', 'equipo', 'rareza', 'posicion']
