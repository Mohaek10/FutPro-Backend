import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from user_app.models import Account
from cartas_app.models import Jugador, JugadorUsuario, Equipo
from ventas_app.models import VentaUsuario, Transaccion


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def create_user(db):
    def make_user(**kwargs):
        return Account.objects.create_user(**kwargs)

    return make_user


@pytest.fixture
def create_superuser(db):
    def make_user(**kwargs):
        return Account.objects.create_superuser(**kwargs)

    return make_user


@pytest.fixture
def user(create_user):
    return create_user(
        email='user@example.com',
        username='user',
        first_name='User',
        last_name='Example',
        password='password123'
    )


@pytest.fixture
def admin_user(create_superuser):
    return create_superuser(
        email='admin@example.com',
        username='admin',
        first_name='Admin',
        last_name='Example',
        password='password123'
    )


@pytest.fixture
def equipo(db):
    return Equipo.objects.create(
        nombre='Equipo Ejemplo',
        liga='Liga Ejemplo',
        pais='Pais Ejemplo',
        escudo='escudo.jpg'
    )


@pytest.fixture
def jugador(db, equipo):
    return Jugador.objects.create(
        nombreCompleto='Jugador Ejemplo',
        edad=25,
        equipo=equipo,
        media=85,
        rareza='Común',
        imagen='imagen.jpg',
        valor=100,
        posicion='DC',
        en_mercado=True,
        isActive=True
    )


@pytest.fixture
def jugador_usuario(db, user, jugador):
    return JugadorUsuario.objects.create(
        usuario=user,
        jugador=jugador,
        cantidad=10
    )


@pytest.fixture
def venta_usuario(db, user, jugador_usuario):
    return VentaUsuario.objects.create(
        vendedor=user,
        jugador_usuario=jugador_usuario,
        cantidad=5,
        precio=200
    )


@pytest.mark.django_db
def test_comprar_mercado_sistema(api_client, user, jugador):
    url = reverse('comprar-sistema')
    api_client.force_authenticate(user=user)
    data = {
        'jugador_id': jugador.id,
        'cantidad': 2
    }
    response = api_client.post(url, data, format='json')
    print(response.data)  # Añadir depuración
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_comprar_mercado_sistema_sin_futcoins(api_client, user, jugador):
    user.futcoins = 50  # Insuficientes FutCoins
    user.save()
    url = reverse('comprar-sistema')
    api_client.force_authenticate(user=user)
    data = {
        'jugador_id': jugador.id,
        'cantidad': 2
    }
    response = api_client.post(url, data, format='json')
    print(response.data)  # Añadir depuración
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'error' in response.data


@pytest.mark.django_db
def test_mercado_usuarios_list(api_client, user, venta_usuario):
    url = reverse('mercado-usuarios')
    api_client.force_authenticate(user=user)
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert response.data


@pytest.mark.django_db
def test_poner_en_venta_usuario(api_client, user, jugador_usuario):
    url = reverse('poner-en-venta-usuario')
    api_client.force_authenticate(user=user)
    data = {
        'jugador_usuario': jugador_usuario.id,
        'cantidad': 3,
        'precio': 150
    }
    response = api_client.post(url, data, format='json')
    assert response.status_code == status.HTTP_201_CREATED
    assert 'id' in response.data


@pytest.mark.django_db
def test_poner_en_venta_mas_de_lo_que_posee(api_client, user, jugador_usuario):
    url = reverse('poner-en-venta-usuario')
    api_client.force_authenticate(user=user)
    data = {
        'jugador_usuario': jugador_usuario.id,
        'cantidad': 20,  # Cantidad mayor a la que posee
        'precio': 150
    }
    response = api_client.post(url, data, format='json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'error' in response.data


@pytest.mark.django_db
def test_comprar_jugador_usuario(api_client, user, venta_usuario, create_user):
    comprador = create_user(
        email='comprador@example.com',
        username='comprador',
        first_name='Comprador',
        last_name='Example',
        password='password123'
    )
    comprador.futcoins = 1000  # Suficientes FutCoins
    comprador.save()
    url = reverse('comprar-jugador-usuario', args=[venta_usuario.id])
    api_client.force_authenticate(user=comprador)
    data = {
        'cantidad': 2
    }
    response = api_client.post(url, data, format='json')
    assert response.status_code == status.HTTP_200_OK
    assert 'success' in response.data


@pytest.mark.django_db
def test_comprar_jugador_usuario_sin_futcoins(api_client, user, venta_usuario, create_user):
    comprador = create_user(
        email='comprador@example.com',
        username='comprador',
        first_name='Comprador',
        last_name='Example',
        password='password123'
    )
    comprador.futcoins = 50  # Insuficientes FutCoins
    comprador.save()
    url = reverse('comprar-jugador-usuario', args=[venta_usuario.id])
    api_client.force_authenticate(user=comprador)
    data = {
        'cantidad': 2
    }
    response = api_client.post(url, data, format='json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'error' in response.data


@pytest.mark.django_db
def test_eliminar_jugador_del_mercado(api_client, user, venta_usuario):
    url = reverse('eliminar-venta-usuario', args=[venta_usuario.id])
    api_client.force_authenticate(user=user)
    response = api_client.delete(url)
    assert response.status_code == status.HTTP_200_OK
    assert 'success' in response.data


@pytest.mark.django_db
def test_eliminar_jugador_del_mercado_no_autorizado(api_client, create_user, venta_usuario):
    otro_usuario = create_user(
        email='otro@example.com',
        username='otro',
        first_name='Otro',
        last_name='Usuario',
        password='password123'
    )
    url = reverse('eliminar-venta-usuario', args=[venta_usuario.id])
    api_client.force_authenticate(user=otro_usuario)
    response = api_client.delete(url)
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert 'error' in response.data


@pytest.mark.django_db
def test_transacciones_usuario_list(api_client, user, venta_usuario):
    url = reverse('transacciones-usuario')
    api_client.force_authenticate(user=user)
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert response.data


@pytest.mark.django_db
def test_transacciones_usuario_list_no_autenticado(api_client, venta_usuario):
    url = reverse('transacciones-usuario')
    response = api_client.get(url)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_transacciones_admin_list(api_client, admin_user, venta_usuario):
    url = reverse('transacciones-admin')
    api_client.force_authenticate(user=admin_user)
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert response.data


@pytest.mark.django_db
def test_mercado_usuarios_list_con_filtro(api_client, user, venta_usuario):
    url = f"{reverse('mercado-usuarios')}?search=Jugador Ejemplo"
    api_client.force_authenticate(user=user)
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert response.data


@pytest.mark.django_db
def test_comprar_mercado_sistema_con_cantidad_negativa(api_client, user, jugador):
    url = reverse('comprar-sistema')
    api_client.force_authenticate(user=user)
    data = {
        'jugador_id': jugador.id,
        'cantidad': -1  # Cantidad negativa
    }
    response = api_client.post(url, data, format='json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'cantidad' in response.data


@pytest.mark.django_db
def test_comprar_mercado_sistema_jugador_no_activo(api_client, user, jugador):
    jugador.isActive = False
    jugador.save()
    url = reverse('comprar-sistema')
    api_client.force_authenticate(user=user)
    data = {
        'jugador_id': jugador.id,
        'cantidad': 2
    }
    response = api_client.post(url, data, format='json')
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert 'detail' in response.data


@pytest.mark.django_db
def test_poner_en_venta_usuario_jugador_no_pertenece(api_client, create_user, jugador_usuario):
    otro_usuario = create_user(
        email='otro@example.com',
        username='otro',
        first_name='Otro',
        last_name='Usuario',
        password='password123'
    )
    url = reverse('poner-en-venta-usuario')
    api_client.force_authenticate(user=otro_usuario)
    data = {
        'jugador_usuario': jugador_usuario.id,
        'cantidad': 3,
        'precio': 150
    }
    response = api_client.post(url, data, format='json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_mercado_usuarios_list_no_autenticado(api_client):
    url = reverse('mercado-usuarios')
    response = api_client.get(url)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_comprar_jugador_usuario_inactivo(api_client, user, venta_usuario, create_user):
    comprador = create_user(
        email='comprador@example.com',
        username='comprador',
        first_name='Comprador',
        last_name='Example',
        password='password123'
    )
    comprador.futcoins = 1000  # Suficientes FutCoins
    comprador.save()
    venta_usuario.isActive = False
    venta_usuario.save()
    url = reverse('comprar-jugador-usuario', args=[venta_usuario.id])
    api_client.force_authenticate(user=comprador)
    data = {
        'cantidad': 2
    }
    response = api_client.post(url, data, format='json')
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert 'detail' in response.data


@pytest.mark.django_db
def test_eliminar_jugador_del_mercado_inactivo(api_client, user, venta_usuario):
    venta_usuario.isActive = False
    venta_usuario.save()
    url = reverse('eliminar-venta-usuario', args=[venta_usuario.id])
    api_client.force_authenticate(user=user)
    response = api_client.delete(url)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert 'detail' in response.data


@pytest.mark.django_db
def test_transacciones_admin_list_no_autenticado(api_client):
    url = reverse('transacciones-admin')
    response = api_client.get(url)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_transacciones_admin_list_usuario_normal(api_client, user):
    url = reverse('transacciones-admin')
    api_client.force_authenticate(user=user)
    response = api_client.get(url)
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_comprar_mercado_sistema_sin_autenticar(api_client, jugador):
    url = reverse('comprar-sistema')
    data = {
        'jugador_id': jugador.id,
        'cantidad': 2
    }
    response = api_client.post(url, data, format='json')
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_poner_en_venta_usuario_sin_autenticar(api_client, jugador_usuario):
    url = reverse('poner-en-venta-usuario')
    data = {
        'jugador_usuario': jugador_usuario.id,
        'cantidad': 3,
        'precio': 150
    }
    response = api_client.post(url, data, format='json')
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_eliminar_jugador_del_mercado_sin_autenticar(api_client, venta_usuario):
    url = reverse('eliminar-venta-usuario', args=[venta_usuario.id])
    response = api_client.delete(url)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_comprar_jugador_usuario_cantidad_negativa(api_client, user, venta_usuario, create_user):
    comprador = create_user(
        email='comprador@example.com',
        username='comprador',
        first_name='Comprador',
        last_name='Example',
        password='password123'
    )
    comprador.futcoins = 1000  # Suficientes FutCoins
    comprador.save()
    url = reverse('comprar-jugador-usuario', args=[venta_usuario.id])
    api_client.force_authenticate(user=comprador)
    data = {
        'cantidad': -1  # Cantidad negativa
    }
    response = api_client.post(url, data, format='json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST
