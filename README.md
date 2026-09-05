# 🛒 E-Commerce REST API

A production-deployed REST API for an e-commerce platform, built with **Django REST Framework** — covering catalog, cart, orders, and live payments with Razorpay.

## 🚀 Live

|                        |                                                                   |
| ---------------------- | ----------------------------------------------------------------- |
| **API docs (ReDoc)**   | https://ecommerce-api-production-695c8.up.railway.app/api/redoc/  |
| **API docs (Swagger)** | https://ecommerce-api-production-695c8.up.railway.app/api/docs/   |
| **OpenAPI schema**     | https://ecommerce-api-production-695c8.up.railway.app/api/schema/ |
| **Base URL**           | `https://ecommerce-api-production-695c8.up.railway.app`           |

## ⚙️ Tech Stack

- **Python 3.11**, **Django 5.2** + Django REST Framework 3.17
- **PostgreSQL** (Neon) with connection pooling via `dj-database-url`sssss
- **Redis** for caching and as the Celery broker
- **Celery** for background tasks (email, invoices, webhook processing)
- **JWT** auth via `djangorestframework-simplejwt` (15-min access tokens, refresh rotation)
- **Razorpay** payment gateway with HMAC-SHA256 webhook verification
- **drf-spectacular** for OpenAPI 3 schema generation
- **Gunicorn** + **WhiteNoise**, deployed on **Railway**
- **pytest** + **GitHub Actions** CI

## 📦 Features

**Catalog & orders**

- Product and category management with seller ownership rules
- Shopping cart with add/update/remove
- Order placement and status tracking

**Auth & access control**

- JWT registration and login with refresh-token rotation
- Three-tier role-based access (buyer / seller / admin)
- Sliding-window rate limiting — 15-minute lockout after 5 failed logins

**Payments**

- Razorpay order creation and payment verification
- HMAC-SHA256 signature verification on every incoming webhook, so forged callbacks are rejected
- Idempotency key derived from `order_id + payment_id + amount`, so a retried webhook can never produce a duplicate charge

**Performance & async**

- Email, invoice generation, and webhook handling offloaded to Celery + Redis, keeping API responses under 100ms
- N+1 queries eliminated with `select_related` / `prefetch_related`
- Composite indexes on the hot query paths
- Connection pool resized after diagnosing pool exhaustion under load

**Quality**

- pytest suite with high coverage on the payment and order paths
- GitHub Actions running the full suite on every commit

## 🏗️ Engineering Notes

Three problems worth reading the code for:

**Connection pool exhaustion.** Under load testing, latency climbed to ~800ms and requests began timing out. The cause was two-fold: N+1 queries multiplying the query count per request, and an oversized connection pool causing contention rather than relieving it. Fixing the query patterns and _reducing_ the pool size brought latency to ~120ms — counterintuitive, but the pool was the bottleneck, not the relief.

**Duplicate-charge prevention.** Razorpay retries webhooks on non-2xx responses, so the same payment event can arrive several times. Every webhook is verified with HMAC-SHA256 against the shared secret first, then deduplicated with an idempotency key hashed from the order, payment, and amount. Replays are recognized and discarded rather than reprocessed.

**Keeping the request path fast.** Anything that doesn't need to happen before the response — sending mail, generating invoices, post-processing webhooks — is dispatched to Celery. The API returns immediately and the worker finishes out of band.

## 🛠️ Local Setup

```bash
git clone https://github.com/kumarvijay35/ecommerce-api.git
cd ecommerce-api
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env             # fill in your values
python manage.py migrate
python manage.py runserver
```

Celery worker (separate terminal, requires Redis running):

```bash
celery -A core worker -l info
```

## 🔑 Environment Variables

| Variable              | Description                                        |
| --------------------- | -------------------------------------------------- |
| `DJANGO_SECRET_KEY`   | Django secret key                                  |
| `DEBUG`               | `False` in production                              |
| `DATABASE_URL`        | PostgreSQL connection string                       |
| `REDIS_URL`           | Redis connection string (cache + Celery broker)    |
| `RAZORPAY_KEY_ID`     | Razorpay public key                                |
| `RAZORPAY_KEY_SECRET` | Razorpay secret — never commit                     |
| `ALLOWED_HOSTS`       | Comma-separated allowed hosts                      |
| `EMAIL_HOST_USER`     | SMTP user (falls back to console backend if unset) |
| `EMAIL_HOST_PASSWORD` | SMTP password                                      |

## 📡 API Endpoints

Full interactive reference: **[/api/redoc/](https://ecommerce-api-production-695c8.up.railway.app/api/redoc/)**

| Method          | Endpoint                      | Description             | Auth   |
| --------------- | ----------------------------- | ----------------------- | ------ |
| POST            | `/api/users/register/`        | Register new user       | No     |
| POST            | `/api/users/login/`           | Login and receive JWT   | No     |
| GET/PUT         | `/api/users/profile/`         | View/edit profile       | Yes    |
| GET             | `/api/products/`              | List products           | No     |
| POST            | `/api/products/`              | Create product          | Seller |
| GET             | `/api/products/<id>/`         | Product detail          | No     |
| PUT/DELETE      | `/api/products/<id>/`         | Edit/delete product     | Owner  |
| GET             | `/api/products/my-products/`  | Seller's own products   | Seller |
| GET/POST/DELETE | `/api/orders/cart/`           | Cart operations         | Yes    |
| POST            | `/api/orders/place-order/`    | Place order             | Yes    |
| POST            | `/api/orders/verify-payment/` | Verify Razorpay payment | Yes    |
| GET             | `/api/orders/my-orders/`      | Order history           | Yes    |

## 🧪 Running Tests

```bash
pytest tests/ -v
```

## 📄 License

MIT
