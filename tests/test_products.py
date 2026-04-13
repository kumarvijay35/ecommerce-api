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
def seller(db):
    return User.objects.create_user(
        username='seller1', email='seller@example.com',
        password='pass1234', is_seller=True
    )


@pytest.fixture
def buyer(db):
    return User.objects.create_user(
        username='buyer1', email='buyer@example.com',
        password='pass1234', is_seller=False
    )


@pytest.fixture
def category(db):
    return Category.objects.create(name='Electronics')


@pytest.fixture
def product(db, seller, category):
    return Product.objects.create(
        seller=seller, category=category,
        name='Laptop', description='A great laptop',
        price=50000, stock=10
    )


@pytest.mark.django_db
def test_list_products_public(client, product):
    url = reverse('product-list')
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_create_product_as_seller(client, seller, category):
    client.force_authenticate(user=seller)
    url = reverse('product-list')
    data = {
        'name': 'Phone',
        'description': 'A good phone',
        'price': 20000,
        'stock': 5,
        'category': category.id
    }
    response = client.post(url, data)
    assert response.status_code == 201
    assert response.data['name'] == 'Phone'


@pytest.mark.django_db
def test_create_product_as_buyer_fails(client, buyer, category):
    client.force_authenticate(user=buyer)
    url = reverse('product-list')
    data = {
        'name': 'Phone',
        'description': 'A good phone',
        'price': 20000,
        'stock': 5,
        'category': category.id
    }
    response = client.post(url, data)
    assert response.status_code == 403


@pytest.mark.django_db
def test_product_detail(client, product):
    url = reverse('product-detail', kwargs={'pk': product.id})
    response = client.get(url)
    assert response.status_code == 200
    assert response.data['name'] == 'Laptop'