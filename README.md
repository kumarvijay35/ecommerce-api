# 🛒 E-Commerce API

A full-featured REST API for an e-commerce platform built with **Django REST Framework**.

## 🚀 Live API

Base URL: `https://ecommerce-api-796y.onrender.com`
Swagger Docs: `https://ecommerce-api-796y.onrender.com/api/docs/`

## ⚙️ Tech Stack

- Python 3.10+
- Django 4.x + Django REST Framework
- PostgreSQL
- JWT Authentication
- Razorpay Payment Gateway
- Deployed on Render

## 📦 Features

- User registration & JWT login
- Product & category management
- Role-based access (buyer / seller)
- Shopping cart
- Order placement & tracking
- Razorpay payment integration
- Swagger API documentation
- Full test suite with pytest

## 🛠️ Local Setup

```bash
git clone https://github.com/YOUR_USERNAME/ecommerce-api.git
cd ecommerce-api
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # fill in your values
python manage.py migrate
python manage.py runserver
```

## 🔑 Environment Variables

SECRET_KEY=
DEBUG=
DATABASE_URL=
RAZORPAY_KEY_ID=
RAZORPAY_KEY_SECRET=
ALLOWED_HOSTS=

## 📡 API Endpoints

| Method          | Endpoint                      | Description         | Auth   |
| --------------- | ----------------------------- | ------------------- | ------ |
| POST            | `/api/users/register/`        | Register new user   | No     |
| POST            | `/api/users/login/`           | Login & get token   | No     |
| GET/PUT         | `/api/users/profile/`         | View/edit profile   | Yes    |
| GET             | `/api/products/`              | List all products   | No     |
| POST            | `/api/products/`              | Create product      | Seller |
| GET             | `/api/products/<id>/`         | Product detail      | No     |
| PUT/DELETE      | `/api/products/<id>/`         | Edit/delete product | Owner  |
| GET             | `/api/products/my-products/`  | My products         | Seller |
| GET/POST/DELETE | `/api/orders/cart/`           | Cart operations     | Yes    |
| POST            | `/api/orders/place-order/`    | Place order         | Yes    |
| POST            | `/api/orders/verify-payment/` | Verify Razorpay     | Yes    |
| GET             | `/api/orders/my-orders/`      | My orders           | Yes    |

## 🧪 Running Tests

```bash
pytest tests/ -v
```
