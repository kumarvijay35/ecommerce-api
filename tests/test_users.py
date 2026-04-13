# Create your tests here.
from django.test import TestCase
import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from users.models import User


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def create_user(db):
    def make_user(**kwargs):
        return User.objects.create_user(
            username=kwargs.get('username', 'testuser'),
            email=kwargs.get('email', 'test@example.com'),
            password=kwargs.get('password', 'testpass123'),
        )
    return make_user


@pytest.mark.django_db
def test_user_registration(client):
    url = reverse('register')
    data = {
        'username': 'newuser',
        'email': 'newuser@example.com',
        'password': 'newpass123',
    }
    response = client.post(url, data)
    assert response.status_code == 201


@pytest.mark.django_db
def test_user_login(client, create_user):
    create_user(email='login@example.com', password='pass1234')
    url = reverse('login')
    data = {'email': 'login@example.com', 'password': 'pass1234'}
    response = client.post(url, data)
    assert response.status_code == 200
    assert 'access' in response.data


@pytest.mark.django_db
def test_login_wrong_password(client, create_user):
    create_user(email='wrong@example.com', password='correctpass')
    url = reverse('login')
    response = client.post(url, {'email': 'wrong@example.com', 'password': 'wrongpass'})
    assert response.status_code == 401


@pytest.mark.django_db
def test_profile_requires_auth(client):
    url = reverse('profile')
    response = client.get(url)
    assert response.status_code == 401


@pytest.mark.django_db
def test_profile_authenticated(client, create_user):
    user = create_user()
    client.force_authenticate(user=user)
    url = reverse('profile')
    response = client.get(url)
    assert response.status_code == 200
    assert response.data['email'] == user.email