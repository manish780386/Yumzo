
# Yumzo Backend

Subscription-based tiffin/food delivery backend for Indore — cloud kitchens within 3km clusters, own riders, student/PG focus.

## Tech Stack

- **Framework:** Django 5 + Django REST Framework
- **Auth:** Phone OTP + JWT (`djangorestframework-simplejwt`)
- **Async/Real-time:** Django Channels + Daphne (live rider tracking over WebSocket)
- **Background jobs:** Celery + Redis (daily order auto-generation, subscription expiry)
- **Database:** SQLite for local dev (switch to PostgreSQL for production)

## Project Structure

```
yumzo_backend/
├── manage.py
├── requirements.txt
├── .env                        # secrets — never commit this
│
├── yumzo_backend/              # project config
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py                 # Channels + Daphne entrypoint
│   ├── wsgi.py
│   └── celery.py
│
├── users/                      # auth, roles, profile
├── kitchens/                   # cloud kitchen clusters, menu, reviews
├── subscriptions/               # plans, pause/skip, wallet
├── orders/                     # daily meal orders + Celery auto-generation
└── delivery/                   # riders, captains, batches, live tracking
```

Each app follows the same internal layout: `models.py`, `serializers.py`, `views.py`, `urls.py`, `admin.py`.

## Setup

### 1. Clone and create virtual environment

```bash
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # macOS/Linux
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

> **Note:** `psycopg2-binary` is commented out by default since it needs PostgreSQL installed to build on Windows. Local dev runs fine on SQLite without it — uncomment it only once Postgres is set up.

### 3. Configure environment variables

```bash
copy .env.example .env          # Windows
# cp .env.example .env          # macOS/Linux
```

Open `.env` and set a real `SECRET_KEY`. Generate one with:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 4. Run migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Create an admin user

```bash
python manage.py createsuperuser
```

### 6. Run the server

Because this project uses Channels (WebSockets for live rider tracking), run it with **Daphne**, not `manage.py runserver`:

```bash
python -m daphne -b 0.0.0.0 -p 8000 yumzo_backend.asgi:application
```

Visit `http://127.0.0.1:8000/admin/` to confirm it's working.

### 7. Redis (required for Celery + Channels)

Install and run Redis locally, or via Docker:

```bash
docker run -p 6379:6379 redis
```

### 8. Run Celery (separate terminal, for daily order generation)

```bash
celery -A yumzo_backend worker -l info
celery -A yumzo_backend beat -l info
```

## API Endpoints

### Auth (`/api/users/`)

| Method    | Endpoint              | Description                                     |
| --------- | --------------------- | ----------------------------------------------- |
| POST      | `auth/request-otp/` | Send OTP to phone number                        |
| POST      | `auth/verify-otp/`  | Verify OTP, returns JWT access + refresh tokens |
| GET/PATCH | `profile/`          | Get/update logged-in user's profile             |

### Kitchens (`/api/kitchens/`)

| Method | Endpoint              | Description                                       |
| ------ | --------------------- | ------------------------------------------------- |
| GET    | `nearby/?lat=&lng=` | Cloud kitchens whose 3km radius covers this point |
| GET    | `<id>/`             | Kitchen detail + menu                             |

### Subscriptions (`/api/subscriptions/`)

| Method | Endpoint             | Description                         |
| ------ | -------------------- | ----------------------------------- |
| GET    | `plans/`           | List available subscription plans   |
| POST   | `subscribe/`       | Create a new subscription           |
| GET    | `my-subscription/` | Current active subscription         |
| POST   | `pause/`           | Pause subscription for a date range |
| POST   | `skip-meal/`       | Skip a single scheduled meal        |
| GET    | `wallet/`          | Wallet balance                      |

### Orders (`/api/orders/`)

| Method | Endpoint            | Description                     |
| ------ | ------------------- | ------------------------------- |
| GET    | `today/`          | Today's scheduled meals         |
| GET    | `history/`        | Past order history              |
| POST   | `mark-delivered/` | Rider confirms delivery via OTP |

### Delivery (`/api/delivery/`)

| Method | Endpoint             | Description                                                  |
| ------ | -------------------- | ------------------------------------------------------------ |
| POST   | `update-location/` | Rider pushes current lat/lng (also broadcasts via WebSocket) |
| GET    | `my-batches/`      | Rider's assigned delivery batches for today                  |
| GET    | `my-team/`         | Captain's view of their assigned riders                      |

### WebSocket

| URL                      | Description                                        |
| ------------------------ | -------------------------------------------------- |
| `ws/track/<batch_id>/` | Live rider location broadcast for a delivery batch |

## Core Background Jobs (`orders/tasks.py`)

- **`generate_tomorrows_orders`** — runs nightly (9 PM), creates tomorrow's `Order` rows for every active, non-paused subscription based on their enabled meal times.
- **`expire_old_subscriptions`** — runs daily (12:05 AM), flips subscriptions past `end_date` to `EXPIRED`.

## Troubleshooting Notes

- **`SECRET_KEY must not be empty`** → make sure `.env` exists with a real `SECRET_KEY`, and `settings.py` is the full file (not just the custom config snippet).
- **`cannot import name 'config' from 'decouple'`** → wrong package installed. Run `pip uninstall decouple python-decouple -y` then `pip install python-decouple`.
- **`No module named 'rest_framework_simplejwt'`** after installing `rest_framework_simplejwt`** → that's a different, unrelated package. Uninstall it and install `djangorestframework-simplejwt` instead.
- **`psycopg2-binary` fails to build (`pg_config not found`)** → PostgreSQL isn't installed locally. Skip it and stay on SQLite for dev, or install PostgreSQL first.
- **`daphne: command not found`** → venv isn't activated, or use `python -m daphne ...` instead of the bare `daphne` command.
- Always run `pip install -r requirements.txt` from inside the activated venv, and avoid installing individual packages by guessing names — naming collisions on PyPI (like the two issues above) are easy to hit.

## Roadmap (not yet built)

- PostGIS-based geo queries (replace current haversine-loop kitchen matching once kitchen count grows)
- Rider route optimization / smart batching logic
- Roommate wallet split
- Referral system
- Razorpay/UPI payment integration
- Production deployment config (Gunicorn + Nginx, Postgres, environment hardening)
