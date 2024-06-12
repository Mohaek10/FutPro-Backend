import pytest
from rest_framework.test import APIClient
from django.urls import reverse
from user_app.models import Account
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken


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


@pytest.mark.django_db
def test_register(api_client):
    url = reverse('register')
    data = {
        'username': 'newuser',
        'email': 'newuser@example.com',
        'password': 'password123',
        'password2': 'password123',
        'first_name': 'New',
        'last_name': 'User',
        'phone_number': '1234567890',
        'futcoins': 0.0
    }
    response = api_client.post(url, data, format='json')
    assert response.status_code == status.HTTP_201_CREATED
    assert 'token' in response.data


@pytest.mark.django_db
def test_login(api_client, user):
    url = reverse('login')
    data = {
        'email': user.email,
        'password': 'password123'
    }
    response = api_client.post(url, data, format='json')
    assert response.status_code == status.HTTP_200_OK
    assert 'token' in response.data


@pytest.mark.django_db
def test_logout(api_client, user):
    url = reverse('login')
    data = {
        'email': user.email,
        'password': 'password123'
    }
    login_response = api_client.post(url, data, format='json')
    refresh_token = login_response.data['token']['refresh']

    url = reverse('logout')
    data = {
        'refresh': refresh_token
    }
    response = api_client.post(url, data, format='json')
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_check_admin_status(api_client, admin_user):
    url = reverse('login')
    data = {
        'email': admin_user.email,
        'password': 'password123'
    }
    login_response = api_client.post(url, data, format='json')
    access_token = login_response.data['token']['access']

    api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + access_token)
    url = reverse('check-admin-status')
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert response.data['is_admin'] is True


@pytest.mark.django_db
def test_change_password(api_client, user):
    url = reverse('login')
    data = {
        'email': user.email,
        'password': 'password123'
    }
    login_response = api_client.post(url, data, format='json')
    access_token = login_response.data['token']['access']

    api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + access_token)
    url = reverse('user-me-change-password')
    data = {
        'old_password': 'password123',
        'new_password': 'newpassword123'
    }
    response = api_client.post(url, data, format='json')
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_user_profile(api_client, user):
    url = reverse('login')
    data = {
        'email': user.email,
        'password': 'password123'
    }
    login_response = api_client.post(url, data, format='json')
    access_token = login_response.data['token']['access']

    api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + access_token)
    url = reverse('user-me')
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert response.data['email'] == user.email

    new_data = {
        'first_name': 'Updated',
        'last_name': 'User',
        'phone_number': '0987654321'
    }
    response = api_client.put(url, new_data, format='json')
    assert response.status_code == status.HTTP_200_OK
    assert response.data['first_name'] == 'Updated'
    assert response.data['phone_number'] == '0987654321'


@pytest.mark.django_db
def test_register_with_existing_email(api_client, user):
    url = reverse('register')
    data = {
        'username': 'anotheruser',
        'email': user.email, 'password': 'password123',
        'password2': 'password123',
        'first_name': 'Another',
        'last_name': 'User',
        'phone_number': '1234567890',
        'futcoins': 0.0
    }
    response = api_client.post(url, data, format='json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_register_with_mismatched_passwords(api_client):
    url = reverse('register')
    data = {
        'username': 'newuser',
        'email': 'newuser@example.com',
        'password': 'password123',
        'password2': 'differentpassword',
        'first_name': 'New',
        'last_name': 'User',
        'phone_number': '1234567890',
        'futcoins': 0.0
    }
    response = api_client.post(url, data, format='json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'error' in response.data


@pytest.mark.django_db
def test_login_with_invalid_credentials(api_client):
    url = reverse('login')
    data = {
        'email': 'nonexistent@example.com',
        'password': 'wrongpassword'
    }
    response = api_client.post(url, data, format='json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'error_message' in response.data


@pytest.mark.django_db
def test_logout_with_invalid_token(api_client):
    url = reverse('logout')
    data = {
        'refresh': 'invalidtoken'
    }
    response = api_client.post(url, data, format='json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'response' in response.data


@pytest.mark.django_db
def test_check_admin_status_as_non_admin(api_client, user):
    url = reverse('login')
    data = {
        'email': user.email,
        'password': 'password123'
    }
    login_response = api_client.post(url, data, format='json')
    access_token = login_response.data['token']['access']

    api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + access_token)
    url = reverse('check-admin-status')
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert response.data['is_admin'] is False


@pytest.mark.django_db
def test_change_password_with_invalid_old_password(api_client, user):
    url = reverse('login')
    data = {
        'email': user.email,
        'password': 'password123'
    }
    login_response = api_client.post(url, data, format='json')
    access_token = login_response.data['token']['access']

    api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + access_token)
    url = reverse('user-me-change-password')
    data = {
        'old_password': 'wrongpassword',
        'new_password': 'newpassword123'
    }
    response = api_client.post(url, data, format='json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'old_password' in response.data


@pytest.mark.django_db
def test_change_password_with_invalid_new_password(api_client, user):
    url = reverse('login')
    data = {
        'email': user.email,
        'password': 'password123'
    }
    login_response = api_client.post(url, data, format='json')
    access_token = login_response.data['token']['access']

    api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + access_token)
    url = reverse('user-me-change-password')
    data = {
        'old_password': 'password123',
        'new_password': 'short'}
    response = api_client.post(url, data, format='json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'new_password' in response.data


@pytest.mark.django_db
def test_get_user_profile_unauthenticated(api_client):
    url = reverse('user-me')
    response = api_client.get(url)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_update_user_profile_partial(api_client, user):
    url = reverse('login')
    data = {
        'email': user.email,
        'password': 'password123'
    }
    login_response = api_client.post(url, data, format='json')
    access_token = login_response.data['token']['access']

    api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + access_token)
    url = reverse('user-me')
    new_data = {
        'first_name': 'Updated'
    }
    response = api_client.patch(url, new_data, format='json')
    assert response.status_code == status.HTTP_200_OK
    assert response.data['first_name'] == 'Updated'


@pytest.mark.django_db
def test_login_inactive_user(api_client, user):
    user.is_active = False
    user.save()
    url = reverse('login')
    data = {
        'email': user.email,
        'password': 'password123'
    }
    response = api_client.post(url, data, format='json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'error_message' in response.data


@pytest.mark.django_db
def test_register_without_email(api_client):
    url = reverse('register')
    data = {
        'username': 'newuser',
        'password': 'password123',
        'password2': 'password123',
        'first_name': 'New',
        'last_name': 'User',
        'phone_number': '1234567890',
        'futcoins': 0.0
    }
    response = api_client.post(url, data, format='json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_register_without_username(api_client):
    url = reverse('register')
    data = {
        'email': 'newuser@example.com',
        'password': 'password123',
        'password2': 'password123',
        'first_name': 'New',
        'last_name': 'User',
        'phone_number': '1234567890',
        'futcoins': 0.0
    }
    response = api_client.post(url, data, format='json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_register_without_password(api_client):
    url = reverse('register')
    data = {
        'username': 'newuser',
        'email': 'newuser@example.com',
        'password2': 'password123',
        'first_name': 'New',
        'last_name': 'User',
        'phone_number': '1234567890',
        'futcoins': 0.0
    }
    response = api_client.post(url, data, format='json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_login_without_email(api_client, user):
    url = reverse('login')
    data = {
        'password': 'password123'
    }
    response = api_client.post(url, data, format='json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_login_without_password(api_client, user):
    url = reverse('login')
    data = {
        'email': user.email
    }
    response = api_client.post(url, data, format='json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_update_user_profile_with_invalid_data(api_client, user):
    url = reverse('login')
    data = {
        'email': user.email,
        'password': 'password123'
    }
    login_response = api_client.post(url, data, format='json')
    access_token = login_response.data['token']['access']

    api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + access_token)
    url = reverse('user-me')
    new_data = {
        'email': 'invalidemail'
    }
    response = api_client.put(url, new_data, format='json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_logout_without_refresh_token(api_client):
    url = reverse('logout')
    response = api_client.post(url, {}, format='json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_check_admin_status_unauthenticated(api_client):
    url = reverse('check-admin-status')
    response = api_client.get(url)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_change_password_with_mismatched_new_passwords(api_client, user):
    url = reverse('login')
    data = {
        'email': user.email,
        'password': 'password123'
    }
    login_response = api_client.post(url, data, format='json')
    access_token = login_response.data['token']['access']

    api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + access_token)
    url = reverse('user-me-change-password')
    data = {
        'old_password': 'password123',
        'new_password': 'newpassword123',
        'new_password2': 'differentpassword'
    }
    response = api_client.post(url, data, format='json')
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_get_user_profile_with_invalid_token(api_client):
    api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + 'invalidtoken')
    url = reverse('user-me')
    response = api_client.get(url)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_get_user_profile_as_admin(api_client, admin_user):
    url = reverse('login')
    data = {
        'email': admin_user.email,
        'password': 'password123'
    }
    login_response = api_client.post(url, data, format='json')
    access_token = login_response.data['token']['access']

    api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + access_token)
    url = reverse('user-me')
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert response.data['email'] == admin_user.email


@pytest.mark.django_db
def test_delete_user(api_client, user):
    url = reverse('login')
    data = {
        'email': user.email,
        'password': 'password123'
    }
    login_response = api_client.post(url, data, format='json')
    access_token = login_response.data['token']['access']

    api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + access_token)
    delete_url = reverse('user-me')
    response = api_client.delete(delete_url)
    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED


@pytest.mark.django_db
def test_register_without_email(api_client):
    url = reverse('register')
    data = {
        'username': 'newuser',
        'password': 'password123',
        'password2': 'password123',
        'first_name': 'New',
        'last_name': 'User',
        'phone_number': '1234567890',
        'futcoins': 0.0
    }
    response = api_client.post(url, data, format='json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_register_without_username(api_client):
    url = reverse('register')
    data = {
        'email': 'newuser@example.com',
        'password': 'password123',
        'password2': 'password123',
        'first_name': 'New',
        'last_name': 'User',
        'phone_number': '1234567890',
        'futcoins': 0.0
    }
    response = api_client.post(url, data, format='json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_register_without_password(api_client):
    url = reverse('register')
    data = {
        'username': 'newuser',
        'email': 'newuser@example.com',
        'password2': 'password123',
        'first_name': 'New',
        'last_name': 'User',
        'phone_number': '1234567890',
        'futcoins': 0.0
    }
    response = api_client.post(url, data, format='json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_register_with_existing_email(api_client, user):
    url = reverse('register')
    data = {
        'username': 'newuser',
        'email': user.email,
        'password': 'password123',
        'password2': 'password123',
        'first_name': 'New',
        'last_name': 'User',
        'phone_number': '1234567890',
        'futcoins': 0.0
    }
    response = api_client.post(url, data, format='json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_login_with_wrong_password(api_client, user):
    url = reverse('login')
    data = {
        'email': user.email,
        'password': 'wrongpassword'
    }
    response = api_client.post(url, data, format='json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_update_user_profile_with_invalid_data(api_client, user):
    url = reverse('login')
    data = {
        'email': user.email,
        'password': 'password123'
    }
    login_response = api_client.post(url, data, format='json')
    access_token = login_response.data['token']['access']

    api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + access_token)
    url = reverse('user-me')
    new_data = {
        'email': 'invalidemail'
    }
    response = api_client.put(url, new_data, format='json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_update_user_profile_unauthenticated(api_client):
    url = reverse('user-me')
    new_data = {
        'first_name': 'Updated',
        'last_name': 'User',
        'phone_number': '0987654321'
    }
    response = api_client.put(url, new_data, format='json')
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_logout_without_refresh_token(api_client):
    url = reverse('logout')
    response = api_client.post(url, {}, format='json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_check_admin_status_unauthenticated(api_client):
    url = reverse('check-admin-status')
    response = api_client.get(url)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_change_password_with_mismatched_new_passwords(api_client, user):
    url = reverse('login')
    data = {
        'email': user.email,
        'password': 'password123'
    }
    login_response = api_client.post(url, data, format='json')
    access_token = login_response.data['token']['access']

    api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + access_token)
    url = reverse('user-me-change-password')
    data = {
        'old_password': 'password123',
        'new_password': 'newpassword123',
        'new_password2': 'differentpassword'
    }
    response = api_client.post(url, data, format='json')
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_get_user_profile_with_invalid_token(api_client):
    api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + 'invalidtoken')
    url = reverse('user-me')
    response = api_client.get(url)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_get_user_profile_as_admin(api_client, admin_user):
    url = reverse('login')
    data = {
        'email': admin_user.email,
        'password': 'password123'
    }
    login_response = api_client.post(url, data, format='json')
    access_token = login_response.data['token']['access']

    api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + access_token)
    url = reverse('user-me')
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert response.data['email'] == admin_user.email


@pytest.mark.django_db
def test_delete_user(api_client, user):
    url = reverse('login')
    data = {
        'email': user.email,
        'password': 'password123'
    }
    login_response = api_client.post(url, data, format='json')
    access_token = login_response.data['token']['access']

    api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + access_token)
    delete_url = reverse('user-me')
    response = api_client.delete(delete_url)
    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED


@pytest.mark.django_db
def test_admin_can_view_all_users(api_client, admin_user, user):
    url = reverse('login')
    data = {
        'email': admin_user.email,
        'password': 'password123'
    }
    login_response = api_client.post(url, data, format='json')
    access_token = login_response.data['token']['access']

    api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + access_token)
    list_users_url = reverse('mis-jugadores')
    response = api_client.get(list_users_url)
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) > 0
