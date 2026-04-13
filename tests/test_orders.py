# Create your tests here.
from django.test import TestCase
import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from users.models import User
from products.models import Product, Category


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def user(db):
    return User.objects.create_user(
        username='buyer', email='buyer@example.com', password='pass1234'
    )


@pytest.fixture
def product(db):
    seller = User.objects.create_user(
        username='seller', email='seller@example.com',
        password='pass1234', is_seller=True
    )
    category = Category.objects.create(name='Electronics')
    return Product.objects.create(
        seller=seller, category=category,
        name='Headphones', description='Great sound',
        price=2000, stock=10
    )


@pytest.mark.django_db
def test_view_empty_cart(client, user):
    client.force_authenticate(user=user)
    url = reverse('cart')
    response = client.get(url)
    assert response.status_code == 200
    assert response.data['items'] == []


@pytest.mark.django_db
def test_add_item_to_cart(client, user, product):
    client.force_authenticate(user=user)
    url = reverse('cart')
    response = client.post(url, {'product_id': product.id, 'quantity': 2})
    assert response.status_code == 201
    assert len(response.data['items']) == 1


@pytest.mark.django_db
def test_cart_requires_auth(client):
    url = reverse('cart')
    response = client.get(url)
    assert response.status_code == 401