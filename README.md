
# Yumzo

**Ghar jaisa khana, roz.**

Yumzo is a subscription-based tiffin and meal delivery platform for students and PG/hostel residents in Indore. Instead of Zomato-style one-off orders, subscribers get daily meals on a monthly plan, cooked by partner cloud kitchens inside a fixed 3 km radius and delivered by Yumzo's own riders.

> **Status:** MVP in active development. The subscriber app and the backend are built; the rider app, online payments and push notifications are not yet.

---

## Why this model

|                   | Typical food delivery         | Yumzo                                                |
| ----------------- | ----------------------------- | ---------------------------------------------------- |
| Order pattern     | On-demand, one meal at a time | Monthly subscription, meals scheduled daily          |
| Delivery distance | Anywhere in the city          | Fixed 3 km cluster around each cloud kitchen         |
| Riders            | Gig riders, surge pricing     | Own riders led by a Rider Captain, batched routes    |
| Demand            | Unpredictable                 | Known a day ahead, so kitchens cook the right amount |
| Target user       | Everyone                      | Students and PG residents (dense, repeat customers)  |

Because demand is known in advance, kitchens waste less food, and any leftover portions are sold through **Last-call deals** (25% off from 12:00 noon) instead of being thrown away.

---

## Features

### Subscriber app

- **Phone OTP login** with JWT (access and refresh tokens, auto-refresh on expiry)
- **Profile setup** for new users: name, diet preference (Veg / Non-Veg / Jain / Egg), GPS delivery location
- **Home screen**
  - Today's menu per meal (Breakfast, Lunch, Dinner) with live order status
  - **Last-call deals:** limited surplus portions at 25% off, locked until 12:00 PM, then live
  - Tomorrow's menu preview
  - Skip a meal, with a clear cutoff time shown
- **Plans:** Basic (1 meal/day), Standard (2), Premium (3); subscribe in one tap, matched to the nearest kitchen covering your location
- **My Plan:** status, enabled meals, delivery address, **pause for a date range** (exams, going home)
- **Order history**

### Backend

- Phone OTP auth, custom user with roles (Subscriber, Rider, Captain, Kitchen Owner, Admin)
- Kitchen matching by distance (haversine), 3 km service radius per kitchen
- Daily order auto-generation from active subscriptions (Celery Beat), pause-aware
- Skip and pause logic, skip cutoffs enforced server-side
- Last-call deals with atomic portion counting (cannot oversell)
- Delivery batches, rider and captain models, delivery confirmation by OTP
- Live rider tracking over WebSocket (Django Channels)
- Django admin configured for managing kitchens, menus, deals, subscriptions and orders during the pilot

---

## Tech stack

| Layer           | Tech                                                                        |
| --------------- | --------------------------------------------------------------------------- |
| Mobile app      | React Native (Expo), React Navigation 7, Axios, AsyncStorage, expo-location |
| Backend         | Django 5, Django REST Framework, SimpleJWT                                  |
| Real-time       | Django Channels, Daphne, Redis                                              |
| Background jobs | Celery, Celery Beat, Redis                                                  |
| Database        | SQLite for local development (PostgreSQL planned for production)            |

---

## Project structure

```
yumzo/
├── README.md
│
├── yumzo_backend/                    # Django backend
│   ├── manage.py
│   ├── requirements.txt
│   ├── .env                          # secrets (never commit)
│   ├── yumzo_backend/                # project config
│   │   ├── settings.py
│   │   ├── urls.py
│   │   ├── asgi.py                   # HTTP + WebSocket entrypoint
│   │   ├── wsgi.py
│   │   └── celery.py
│   ├── users/                        # auth, OTP, roles, profile
│   ├── kitchens/                     # cloud kitchens, menu, reviews, last-call deals
│   │   └── management/commands/seed_data.py
│   ├── subscriptions/                # plans, subscriptions, pause, wallet
│   ├── orders/                       # daily orders, claim-deal, Celery tasks
│   │   ├── rules.py                  # skip cutoffs (single place to tune)
│   │   └── tasks.py                  # nightly order generation
│   └── delivery/                     # riders, captains, batches, live tracking
│       ├── consumers.py
│       └── routing.py
│
└── yumzo_app/                        # React Native (Expo) subscriber app
    ├── index.js                      # Expo entry point
    ├── App.js
    ├── app.json
    ├── package.json
    └── src/
        ├── api/
        │   ├── client.js             # Axios instance, JWT + auto refresh
        │   └── endpoints.js          # all backend calls
        ├── context/
        │   └── AuthContext.js        # login state, token storage
        ├── navigation/
        │   └── RootNavigator.js      # auth stack, bottom tabs, app stack
        └── screens/
            ├── PhoneLoginScreen.js
            ├── OTPVerifyScreen.js
            ├── ProfileSetupScreen.js
            ├── HomeScreen.js
            ├── PlansScreen.js
            ├── SubscriptionScreen.js
            └── OrderHistoryScreen.js
```

Each backend app follows the same layout: `models.py`, `serializers.py`, `views.py`, `urls.py`, `admin.py`.

---

## Getting started

### Prerequisites

- Python 3.12 or newer
- Node.js 18 or newer
- Redis (for Celery and Channels), for example `docker run -p 6379:6379 redis`
- Expo Go on a phone, or an Android emulator (Android Studio)

### 1. Backend

```bash
cd yumzo_backend
python -m venv venv
venv\Scripts\activate              # Windows
# source venv/bin/activate         # macOS / Linux

pip install -r requirements.txt
```

Create `.env` next to `manage.py`:

```
SECRET_KEY=your-generated-secret-key
DEBUG=True
REDIS_URL=redis://localhost:6379/0
```

Generate a key with:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Set up the database and test data:

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py seed_data
```

`seed_data` creates one test kitchen near SVVV Indore, a full week of menus (7 days x 3 meals), the three subscription plans, and today's two last-call deals. It is safe to re-run and never duplicates data. **Re-run it each day while testing** to get a fresh set of deals for that day.

Run the server with **Daphne** (not `runserver`, because of the WebSocket support):

```bash
python -m daphne -b 0.0.0.0 -p 8000 yumzo_backend.asgi:application
```

Admin panel: `http://127.0.0.1:8000/admin/`

### 2. Celery (nightly order generation)

In two more terminals (venv activated):

```bash
celery -A yumzo_backend worker -l info --pool=solo     # --pool=solo is required on Windows
celery -A yumzo_backend beat -l info
```

To generate tomorrow's orders immediately while testing:

```bash
python manage.py shell
>>> from orders.tasks import generate_tomorrows_orders
>>> generate_tomorrows_orders()
```

### 3. Mobile app

```bash
cd yumzo_app
npm install
```

Open `src/api/client.js` and set `BASE_URL` to your laptop's **LAN IP** (find it with `ipconfig`):

```js
export const BASE_URL = 'http://192.168.x.x:8000';
```

Then start Expo:

```bash
npx expo start
```

Scan the QR code with Expo Go, or press `a` for the Android emulator.

**Networking checklist**

- Phone/emulator and laptop must be on the **same network** (use a mobile hotspot if your college WiFi isolates devices).
- Allow ports **8000** (backend) and **8081** (Metro) through Windows Firewall.
- The LAN IP changes when you change networks; update `BASE_URL` each time.
- `npx expo start --tunnel` works for Metro only; the backend still needs to be reachable on the LAN.

### Dev-mode OTP

There is no SMS gateway yet. The backend returns the OTP in the API response (`otp_debug`) and the app shows it in an alert ("Dev Mode - OTP"). Remove both before launch (see Roadmap).

---

## API reference

All endpoints are under `/api/` and require `Authorization: Bearer <access_token>` except the OTP and token-refresh endpoints.

### Auth (`/api/users/`, `/api/token/`)

| Method      | Endpoint                    | Description                                        |
| ----------- | --------------------------- | -------------------------------------------------- |
| POST        | `users/auth/request-otp/` | Send OTP to a phone number                         |
| POST        | `users/auth/verify-otp/`  | Verify OTP; returns JWT tokens and `is_new_user` |
| POST        | `token/refresh/`          | Exchange refresh token for a new access token      |
| GET / PATCH | `users/profile/`          | Read or update the logged-in user's profile        |

### Kitchens (`/api/kitchens/`)

| Method | Endpoint              | Description                                                                                                     |
| ------ | --------------------- | --------------------------------------------------------------------------------------------------------------- |
| GET    | `today/`            | **Home screen payload:** today's menu with order status and skip cutoff, last-call deals, tomorrow's menu |
| GET    | `nearby/?lat=&lng=` | Kitchens whose service radius covers a point                                                                    |
| GET    | `<id>/`             | Kitchen detail with menu                                                                                        |

### Subscriptions (`/api/subscriptions/`)

| Method | Endpoint             | Description                                                      |
| ------ | -------------------- | ---------------------------------------------------------------- |
| GET    | `plans/`           | Available plans                                                  |
| POST   | `subscribe/`       | Create a subscription                                            |
| GET    | `my-subscription/` | Active subscription (404 if none)                                |
| POST   | `pause/`           | Pause for a date range; scheduled orders in range become skipped |
| POST   | `skip-meal/`       | Skip one scheduled meal (rejected after the cutoff)              |
| GET    | `wallet/`          | Wallet balance                                                   |

### Orders (`/api/orders/`)

| Method | Endpoint            | Description                                      |
| ------ | ------------------- | ------------------------------------------------ |
| GET    | `today/`          | Today's orders                                   |
| GET    | `history/`        | Past orders                                      |
| POST   | `claim-deal/`     | Buy one portion of a live last-call deal         |
| POST   | `mark-delivered/` | Rider confirms delivery using the customer's OTP |

### Delivery (`/api/delivery/`)

| Method | Endpoint             | Description                                                   |
| ------ | -------------------- | ------------------------------------------------------------- |
| POST   | `update-location/` | Rider pushes current location (also broadcast over WebSocket) |
| GET    | `my-batches/`      | Rider's delivery batches for today                            |
| GET    | `my-team/`         | Captain's view of their riders                                |

### WebSocket

| URL                                       | Description                              |
| ----------------------------------------- | ---------------------------------------- |
| `ws://<host>:8000/ws/track/<batch_id>/` | Live rider location for a delivery batch |

---

## Business rules

All of these are easy to tune once the pilot shows what kitchens and students actually need.

**Skip cutoffs** (`orders/rules.py`), so the kitchen knows the headcount before cooking:

| Meal      | Last time to skip          |
| --------- | -------------------------- |
| Breakfast | 9:00 PM the previous night |
| Lunch     | 9:00 AM the same day       |
| Dinner    | 3:00 PM the same day       |

**Last-call deals** (`LastCallDeal` model, managed from Django admin):

- The kitchen lists surplus portions for a given meal and day.
- Default discount **25%**, live from **12:00 PM** to **9:00 PM** (both configurable per deal).
- Sells only while `portions_left > 0`; claiming is atomic, so it cannot oversell.
- One claim per user per meal per day.
- Only users inside the kitchen's service radius can claim.
- Payment is **pay on delivery** for now.
- Keep the discounted price above the effective per-meal subscription price, otherwise deals cannibalise subscriptions.

**Daily order generation** (Celery Beat):

- 9:00 PM: create tomorrow's orders for every active, non-paused subscription.
- 12:05 AM: mark subscriptions past their end date as expired.

---

## Data model (core)

```
User ──< Subscription >── SubscriptionPlan
              │
              └── CloudKitchen ──< MenuItem
                        │──< LastCallDeal
                        └──< Order >── User
Order ──> DeliveryBatch ──> Rider ──> RiderCaptain
```

Main tables: `User`, `OTPVerification`, `CloudKitchen`, `MenuItem`, `LastCallDeal`, `KitchenReview`, `SubscriptionPlan`, `Subscription`, `PauseRequest`, `Wallet`, `WalletTransaction`, `Order`, `Rider`, `RiderCaptain`, `DeliveryBatch`.

---

## Troubleshooting

| Problem                                                | Fix                                                                                                                               |
| ------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------- |
| `SECRET_KEY must not be empty`                       | Create `.env` with a real `SECRET_KEY`; make sure `settings.py` is the complete file, not just a config snippet             |
| `cannot import name 'config' from 'decouple'`        | Wrong package. Run `pip uninstall decouple python-decouple -y` then `pip install python-decouple`                             |
| `No module named rest_framework_simplejwt`           | A different package was installed. Use `pip install djangorestframework-simplejwt`                                              |
| `psycopg2-binary` fails with `pg_config not found` | PostgreSQL is not installed. Stay on SQLite for development; keep that line commented out in `requirements.txt`                 |
| `daphne` command not found                           | Activate the venv, or use `python -m daphne ...`                                                                                |
| `admin.E403` templates error                         | `settings.py` is missing the `TEMPLATES` block; use the complete settings file                                                |
| App shows a black screen                               | Missing `index.js` entry point. It must call `registerRootComponent(App)`                                                     |
| `Unable to resolve module ../screens/X`              | The screen file is not in `src/screens/` yet                                                                                    |
| "Cannot connect to Expo CLI"                           | Same WiFi/hotspot, allow port 8081 in the firewall, or try `npx expo start --tunnel`                                            |
| "Send OTP" does nothing or errors                      | `BASE_URL` in `client.js` must be your laptop's LAN IP; backend must run with `-b 0.0.0.0`; allow port 8000 in the firewall |
| `ProfileSetup` navigation error                      | `ProfileSetup` must live in the app stack, not the auth stack (login switches stacks as soon as the user is set)                |
| Home shows no menu or deals                            | Run `python manage.py seed_data` (deals are created for the current day only)                                                   |
| `my-subscription` returns 404 in the logs            | Expected when the user has no active subscription                                                                                 |

Install packages from `requirements.txt` instead of guessing names; several PyPI packages share confusingly similar names.

---

## Roadmap

**Before the pilot**

- Test the full flow on a real device with real kitchen data
- Confirm real thali costs with 1-2 kitchens and fix plan and deal prices

**Pilot-phase**

- Meal rating after delivery, feeding a kitchen quality score
- Push notifications ("lunch is out for delivery", "deals are live")
- Menu swap (alternate dish per day)

**Later**

- Rider app (route list, delivery OTP, earnings) and Captain dashboard
- Online payments (Razorpay UPI) and wallet top-ups
- Real SMS OTP via MSG91 / Fast2SMS, then remove `otp_debug` and the dev alert
- PostGIS spatial queries instead of the haversine loop, once kitchens grow past ~50
- Smart delivery batching and route optimisation
- Roommate split billing, referrals and streaks
- Production deployment: PostgreSQL, Gunicorn/Daphne behind Nginx, locked-down CORS and `ALLOWED_HOSTS`, secrets via environment

---

## Security notes

- Never commit `.env`; add it to `.gitignore`.
- `CORS_ALLOW_ALL_ORIGINS` and `ALLOWED_HOSTS = ["*"]` are for development only; restrict them before deploying.
- The OTP debug response must be removed before any real user signs up.

---

Built in Indore.
