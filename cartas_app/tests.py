from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse
from cartas_app.models import Jugador, Equipo, JugadorUsuario, Comentario
from user_app.models import Account
from rest_framework_simplejwt.tokens import RefreshToken


class JugadorAPITestCase(APITestCase):

    def setUp(self):
        self.admin_user = Account.objects.create_superuser(
            first_name='Admin',
            last_name='User',
            username='adminuser',
            email='admin@example.com',
            password='adminpass'
        )
        self.user = Account.objects.create_user(
            first_name='Regular',
            last_name='User',
            username='regularuser',
            email='regular@example.com',
            password='regularpass'
        )
        self.equipo = Equipo.objects.create(
            nombre='Equipo Test',
            liga='Liga Test',
            pais='País Test',
            escudo='http://example.com/escudo.png'
        )
        self.jugador = Jugador.objects.create(
            nombreCompleto='Jugador Test',
            edad=25,
            equipo=self.equipo,
            media=90,
            rareza='Épica',
            valor=1000000.00,
            posicion='DC'
        )
        self.client = APIClient()

    def get_token_for_user(self, user):
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)

    def test_list_jugadores(self):
        url = reverse('jugador-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_jugador_detail_as_authenticated_user(self):
        token = self.get_token_for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        url = reverse('jugador-detail', args=[self.jugador.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_jugador_detail_as_unauthenticated_user(self):
        url = reverse('jugador-detail', args=[self.jugador.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_jugador_as_admin(self):
        token = self.get_token_for_user(self.admin_user)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        url = reverse('jugador-list')
        data = {
            'nombreCompleto': 'Nuevo Jugador',
            'edad': 22,
            'equipo': self.equipo.id,
            'media': 85,
            'rareza': 'Rara',
            'valor': 500000.00,
            'posicion': 'MCO'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_jugador_as_regular_user(self):
        token = self.get_token_for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        url = reverse('jugador-list')
        data = {
            'nombreCompleto': 'Nuevo Jugador',
            'edad': 22,
            'equipo': self.equipo.id,
            'media': 85,
            'rareza': 'Rara',
            'valor': 500000.00,
            'posicion': 'MCO'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_jugador_as_admin(self):
        token = self.get_token_for_user(self.admin_user)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        url = reverse('jugador-detail', args=[self.jugador.id])
        data = {
            'nombreCompleto': 'Jugador Test Actualizado',
            'edad': 26,
            'equipo': self.equipo.id,
            'media': 92,
            'rareza': 'Legendaria',
            'valor': 1200000.00,
            'posicion': 'DC'
        }
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_jugador_as_regular_user(self):
        token = self.get_token_for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        url = reverse('jugador-detail', args=[self.jugador.id])
        data = {
            'nombreCompleto': 'Jugador Test Actualizado',
            'edad': 26,
            'equipo': self.equipo.id,
            'media': 92,
            'rareza': 'Legendaria',
            'valor': 1200000.00,
            'posicion': 'DC'
        }
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_jugador_as_admin(self):
        token = self.get_token_for_user(self.admin_user)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        url = reverse('jugador-detail', args=[self.jugador.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_jugador_as_regular_user(self):
        token = self.get_token_for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        url = reverse('jugador-detail', args=[self.jugador.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_jugadores_with_search(self):
        url = reverse('jugador-list')
        response = self.client.get(url, {'search': 'Jugador Test'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

    def test_list_jugadores_with_ordering(self):
        url = reverse('jugador-list')
        response = self.client.get(url, {'ordering': 'edad'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_jugador_with_partial_data_as_admin(self):
        token = self.get_token_for_user(self.admin_user)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        url = reverse('jugador-detail', args=[self.jugador.id])
        data = {
            'media': 95,
        }
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['media'], 95)


class EquipoAPITestCase(APITestCase):

    def setUp(self):
        self.admin_user = Account.objects.create_superuser(
            first_name='Admin',
            last_name='User',
            username='adminuser',
            email='admin@example.com',
            password='adminpass'
        )
        self.user = Account.objects.create_user(
            first_name='Regular',
            last_name='User',
            username='regularuser',
            email='regular@example.com',
            password='regularpass'
        )
        self.equipo = Equipo.objects.create(
            nombre='Equipo Test',
            liga='Liga Test',
            pais='País Test',
            escudo='http://example.com/escudo.png'
        )
        self.client = APIClient()

    def get_token_for_user(self, user):
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)

    def test_list_equipos(self):
        url = reverse('equipo-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_equipo_detail_as_authenticated_user(self):
        token = self.get_token_for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        url = reverse('equipo-detail', args=[self.equipo.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_equipo_detail_as_unauthenticated_user(self):
        url = reverse('equipo-detail', args=[self.equipo.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_equipo_as_admin(self):
        token = self.get_token_for_user(self.admin_user)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        url = reverse('equipo-list')
        data = {
            'nombre': 'Nuevo Equipo',
            'liga': 'Nueva Liga',
            'pais': 'Nuevo País',
            'escudo': 'http://example.com/nuevo_escudo.png'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_equipo_as_regular_user(self):
        token = self.get_token_for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        url = reverse('equipo-list')
        data = {
            'nombre': 'Nuevo Equipo',
            'liga': 'Nueva Liga',
            'pais': 'Nuevo País',
            'escudo': 'http://example.com/nuevo_escudo.png'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_equipo_as_admin(self):
        token = self.get_token_for_user(self.admin_user)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        url = reverse('equipo-detail', args=[self.equipo.id])
        data = {
            'nombre': 'Equipo Test Actualizado',
            'liga': 'Liga Test Actualizada',
            'pais': 'País Test Actualizado',
            'escudo': 'http://example.com/escudo_actualizado.png'
        }
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_equipo_as_regular_user(self):
        token = self.get_token_for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        url = reverse('equipo-detail', args=[self.equipo.id])
        data = {
            'nombre': 'Equipo Test Actualizado',
            'liga': 'Liga Test Actualizada',
            'pais': 'País Test Actualizado',
            'escudo': 'http://example.com/escudo_actualizado.png'
        }
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_equipo_as_admin(self):
        token = self.get_token_for_user(self.admin_user)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        url = reverse('equipo-detail', args=[self.equipo.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_equipo_as_regular_user(self):
        token = self.get_token_for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        url = reverse('equipo-detail', args=[self.equipo.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_equipos_with_search(self):
        url = reverse('equipo-list')
        response = self.client.get(url, {'search': 'Equipo Test'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

    def test_create_equipo_with_invalid_data_as_admin(self):
        token = self.get_token_for_user(self.admin_user)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        url = reverse('equipo-list')
        data = {
            'nombre': '',
            'liga': 'Nueva Liga',
            'pais': 'Nuevo País',
            'escudo': 'http://example.com/nuevo_escudo.png'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_equipo_with_partial_data_as_admin(self):
        token = self.get_token_for_user(self.admin_user)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        url = reverse('equipo-detail', args=[self.equipo.id])
        data = {
            'nombre': 'Equipo Actualizado'
        }
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['nombre'], 'Equipo Actualizado')


class ComentarioAPITestCase(APITestCase):

    def setUp(self):
        self.admin_user = Account.objects.create_superuser(
            first_name='Admin',
            last_name='User',
            username='adminuser',
            email='admin@example.com',
            password='adminpass'
        )
        self.user = Account.objects.create_user(
            first_name='Regular',
            last_name='User',
            username='regularuser',
            email='regular@example.com',
            password='regularpass'
        )
        self.equipo = Equipo.objects.create(
            nombre='Equipo Test',
            liga='Liga Test',
            pais='País Test',
            escudo='http://example.com/escudo.png'
        )
        self.jugador = Jugador.objects.create(
            nombreCompleto='Jugador Test',
            edad=25,
            equipo=self.equipo,
            media=90,
            rareza='Épica',
            valor=1000000.00,
            posicion='DC'
        )
        self.client = APIClient()

    def get_token_for_user(self, user):
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)

    def test_create_comentario_as_authenticated_user(self):
        token = self.get_token_for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        url = reverse('comentario-create', args=[self.jugador.id])
        data = {
            'calificacion': 5,
            'texto': 'Buen jugador!'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_comentario_as_unauthenticated_user(self):
        url = reverse('comentario-create', args=[self.jugador.id])
        data = {
            'calificacion': 5,
            'texto': 'Buen jugador!'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
