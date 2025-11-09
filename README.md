# MithraPay Backend (Flask + MariaDB + Redis)

This repository is a backend skeleton for **MithraPay** — a system that sells and manages digital subscriptions (Apple Music, Netflix, YouTube Premium, etc.), gift cards, and some physical accessories.  
It is designed with a *clean-ish* architecture in mind:

- **app/core** – config, security (JWT, password hashing), exceptions
- **app/domain** – entities, repository interfaces, service layer
- **app/infrastructure** – SQLAlchemy + MariaDB engine, Redis OTP store, concrete repository implementations
- **app/interfaces/http** – Flask controllers (auth, products, orders, blog, admin) and route registration
- **app/main.py** – Flask app factory

You can run it locally or with Docker (MariaDB + Redis + web).

---

## 1. Requirements

- Python 3.11 (or 3.10+)
- MariaDB / MySQL (we tested with MariaDB Docker image)
- Redis
- `pip install -r requirements.txt`

We use:

- `Flask` for HTTP
- `SQLAlchemy` for ORM
- `mysql-connector-python` for MariaDB
- `redis` for OTP storage
- `python-dotenv` for loading `.env`
- `PyJWT` for token generation

---

## 2. Project Structure

```text
app/
  core/
    config.py          # reads env, DB, Redis, JWT, OTP
    security.py        # password hashing, JWT helpers
    exceptions.py
  domain/
    entities/          # SQLAlchemy models
      blog_posts.py
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
        auth_controller.py
        user_controller.py
        product_controller.py
        order_controller.py
        blog_controller.py
        admin_controller.py
      routes.py
  main.py              # app factory, imports models, create_all
Dockerfile
docker-compose.yml
requirements.txt
.env.example
```

---

## 3. Environment Variables

Create a `.env` in the project root:

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

> **Important:** we added `python-dotenv` and we call `load_dotenv()` in `app/core/config.py`, so these values will actually be picked up.

---

## 4. Database (MariaDB) Notes

We had to ensure the DB user is created with a plugin that Python drivers understand.

If you use Docker (see below), this is done for you.

If you use your own MariaDB, run:

```sql
CREATE DATABASE IF NOT EXISTS mithrapay_DB
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

CREATE USER IF NOT EXISTS 'mithra_user'@'localhost'
  IDENTIFIED BY 'mithra_pass';

GRANT ALL PRIVILEGES ON mithrapay_DB.* TO 'mithra_user'@'localhost';
FLUSH PRIVILEGES;
```

Also make sure your DB default collation is **not** `utf8mb4_0900_ai_ci` if your MariaDB is older. Use:

```sql
ALTER DATABASE mithrapay_DB
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;
```

---

## 5. Running Locally

1. Create and activate venv
2. Install deps:

   ```bash
   pip install -r requirements.txt
   ```

3. Make sure MariaDB and Redis are running and your `.env` is correct.

4. Run:

   ```bash
   python -m flask --app app.main run --debug
   ```

   or simply

   ```bash
   python app/main.py
   ```

5. Visit: http://localhost:5000

You should see:

```json
{
  "app": "MithraPay backend",
  "status": "ok",
  "env": "development"
}
```

---

## 6. Running with Docker

We prepared a `Dockerfile` and `docker-compose.yml`.

- `web` → your Flask app
- `db` → MariaDB
- `redis` → OTP / cache

Run:

```bash
docker compose build
docker compose up
```

Then open http://localhost:5000

The compose file passes these envs to the container:

```yaml
DB_HOST: db
DB_USER: mithra_user
DB_PASS: mithra_pass
DB_NAME: mithrapay_DB
REDIS_URL: redis://redis:6379/0
```

---

## 7. Available Endpoints (current)

- `POST /auth/register`
- `POST /auth/login`
- `POST /auth/request-otp`
- `POST /auth/verify-otp`
- `GET /products/`
- `GET /products/<id>`
- `POST /orders/`
- `GET /orders/<id>`
- `GET /blog/`
- `GET /blog/<slug>`
- `GET /admin/products`
- `POST /admin/products`
- `PUT /admin/products/<id>`

These are **starter** endpoints — the services and repo interfaces are ready for more.

---

## 8. Notes on Clean Architecture

- Controllers (Flask blueprints) call **services**
- Services depend on **repository interfaces** (`app/domain/repositories/...`)
- Infrastructure provides **concrete repos** that use SQLAlchemy
- This lets you unit-test the services with fake repos.

---

## 9. Troubleshooting

- **Foreign key error on startup** → make sure `app/main.py` imports *all* models before `Base.metadata.create_all(...)`.
- **`Unknown collation: 'utf8mb4_0900_ai_ci'`** → your MariaDB is older; set collation to `utf8mb4_unicode_ci` in `maria_engine.py` *and* in the DB.
- **`Access denied for user ...`** → DB user did not exist or wrong DB name; create DB and grant privileges as shown above.
- **`Authentication plugin 'auth_gssapi_client'`** → create a new DB user with `mysql_native_password` (or use the provided Docker MariaDB).

---

## 10. License

Internal / project use.
