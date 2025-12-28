# MithraPay Backend (Flask + MariaDB + Redis)

MithraPay is a backend skeleton for selling and managing digital subscriptions (Apple Music, Netflix, YouTube Premium, etc.), gift cards, and accessories. This repo focuses on **clean-ish architecture** with a clear separation of concerns.

If you are new to Python/Flask, follow the **Quick Start** section first. It uses Docker to give you a working app with minimal setup.

---

## Table of Contents

1. [Tech Stack](#tech-stack)
2. [Project Structure](#project-structure)
3. [Quick Start (Docker)](#quick-start-docker)
4. [Run Locally (No Docker)](#run-locally-no-docker)
5. [Environment Variables](#environment-variables)
6. [Database Notes](#database-notes)
7. [Common Tasks](#common-tasks)
8. [Available Endpoints (Current)](#available-endpoints-current)
9. [Troubleshooting](#troubleshooting)
10. [License](#license)

---

## Tech Stack

- **Python 3.11+**
- **Flask** for HTTP API
- **SQLAlchemy** for ORM
- **MariaDB / MySQL** database
- **Redis** for OTP storage
- **PyJWT** for access tokens

---

## Project Structure

```text
app/
  core/
    config.py          # reads env, DB, Redis, JWT, OTP
    security.py        # password hashing, JWT helpers
    exceptions.py
  domain/
    entities/          # SQLAlchemy models
      blog_post.py
      cart.py
      cart_item.py
      category.py
      order.py
      order_item.py
      payment.py
      product.py
      role.py
      setting.py
      user.py
      user_role.py
    repositories/      # interfaces (ABC) the services depend on
      user_repository.py
      product_repository.py
      order_repository.py
      blog_repository.py
      payment_repository.py
    services/          # business logic
      auth_service.py
      otp_service.py
      product_service.py
      order_service.py
      payment_service.py
      content_service.py
  infrastructure/
    db/
      base.py
      maria_engine.py
      session.py
    redis/
      redis_client.py
      otp_store.py
    repositories/      # SQLAlchemy concrete repos
      user_sqlalchemy.py
      product_sqlalchemy.py
      order_sqlalchemy.py
      blog_sqlalchemy.py
      payment_sqlalchemy.py
  interfaces/
    http/
      controllers/
        __init__.py
        admin_controller.py
        auth_controller.py
        blog_controller.py
        cart_controller.py
        order_controller.py
        product_controller.py
        user_controller.py
      routes.py
  main.py              # app factory, imports models, create_all
Dockerfile
docker-compose.yml
requirements.txt
.env.example
```

---

## Quick Start (Docker)

> **Best for beginners.** This spins up the API + MariaDB + Redis in one command.

### 1) Prerequisites
- [Docker Desktop](https://www.docker.com/products/docker-desktop/)

### 2) Run

```bash
docker compose build
docker compose up
```

### 3) Confirm it works
Open http://localhost:5000 in your browser or run:

```bash
curl http://localhost:5000
```

Expected response:

```json
{
  "app": "MithraPay backend",
  "status": "ok",
  "env": "development"
}
```

The `docker-compose.yml` already sets these environment variables for you:

```yaml
DB_HOST: db
DB_USER: mithra_user
DB_PASS: mithra_pass
DB_NAME: mithrapay_DB
REDIS_URL: redis://redis:6379/0
```

---

## Run Locally (No Docker)

> Use this if you want to run MariaDB and Redis on your own machine.

### 1) Prerequisites
- Python 3.11+ installed
- MariaDB (or MySQL)
- Redis

### 2) Create and activate a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
```

### 3) Install dependencies

```bash
pip install -r requirements.txt
```

### 4) Create your `.env` file

Copy the example and adjust if needed:

```bash
cp .env.example .env
```

### 5) Start MariaDB + Redis
Make sure **MariaDB** and **Redis** are running and reachable by the values in `.env`.

### 6) Run the app

```bash
python -m flask --app app.main run --debug
```

Or:

```bash
python app/main.py
```

### 7) Verify
Visit http://localhost:5000 or:

```bash
curl http://localhost:5000
```

---

## Environment Variables

All values are loaded from `.env` using `python-dotenv`.

```env
# Flask
FLASK_ENV=development
SECRET_KEY=super-secret-key
JWT_SECRET=super-jwt-secret

# MariaDB
DB_HOST=localhost
DB_PORT=3306
DB_USER=mithra_user
DB_PASS=mithra_pass
DB_NAME=mithrapay_DB

# Redis
REDIS_URL=redis://localhost:6379/0

# OTP
OTP_EXPIRE_SECONDS=120
```

---

## Database Notes

- On startup, the app calls `Base.metadata.create_all(...)` to create tables automatically in **development**.
- If you want to manage schema explicitly, you can add Alembic migrations later.

If you are creating your own database manually, use:

```sql
CREATE DATABASE IF NOT EXISTS mithrapay_DB
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

CREATE USER IF NOT EXISTS 'mithra_user'@'localhost'
  IDENTIFIED BY 'mithra_pass';

GRANT ALL PRIVILEGES ON mithrapay_DB.* TO 'mithra_user'@'localhost';
FLUSH PRIVILEGES;
```

---

## Common Tasks

### Create a user (example)

```bash
curl -X POST http://localhost:5000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"name": "Jane", "email": "jane@example.com", "password": "Password123"}'
```

### Login (example)

```bash
curl -X POST http://localhost:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "jane@example.com", "password": "Password123"}'
```

---

## Available Endpoints (Current)

> These are starter endpoints you can build on.

- `POST /auth/register`
- `POST /auth/login`
- `POST /auth/request-otp`
- `POST /auth/verify-otp`
- `GET /users/me`
- `PUT /users/me`
- `GET /products/`
- `GET /products/<id>`
- `POST /orders/`
- `GET /orders/<id>`
- `GET /blog/`
- `GET /blog/<slug>`
- `GET /admin/products`
- `POST /admin/products`
- `PUT /admin/products/<id>`
- `GET /cart/<user_id>`
- `POST /cart/items`
- `PUT /cart/items/<item_id>`
- `DELETE /cart/items/<item_id>`
- `DELETE /cart/<user_id>`

---

## Troubleshooting

- **Foreign key error on startup** → ensure `app/main.py` imports *all* models before `Base.metadata.create_all(...)`.
- **`Unknown collation: 'utf8mb4_0900_ai_ci'`** → your MariaDB is older; set collation to `utf8mb4_unicode_ci` in `maria_engine.py` *and* in the DB.
- **`Access denied for user ...`** → DB user did not exist or wrong DB name; create DB and grant privileges as shown above.
- **`Authentication plugin 'auth_gssapi_client'`** → create a new DB user with `mysql_native_password` (or use the provided Docker MariaDB).

---

## License

Internal / project use.
