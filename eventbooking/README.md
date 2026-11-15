# EventHub — Event Ticket Booking System

## HackerRank-Style Backend Debugging Challenge

### Overview

You are a backend developer at **EventHub**, an event ticket booking platform. A previous developer implemented the initial backend but left before completing all validation logic and exception handling.

The backend currently has partial functionality — some operations work superficially but skip critical business validations, creating data integrity issues and security vulnerabilities.

**Your task**: Examine the project, identify the bugs, and fix them so that all tests pass.

---

### Project Structure

```
eventbooking/
├── manage.py
├── requirements.txt
├── pytest.ini
├── eventbooking/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── exceptions.py          # Custom exception classes
├── events/
│   ├── __init__.py
│   ├── apps.py
│   ├── admin.py
│   ├── models.py               # Event, TicketType models
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   └── services/
│       ├── __init__.py
│       └── event_service.py    # Event retrieval logic
├── bookings/
│   ├── __init__.py
│   ├── apps.py
│   ├── admin.py
│   ├── models.py               # Booking model
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   ├── utils/
│   │   ├── __init__.py
│   │   └── pricing.py          # Price calculation utilities
│   └── services/
│       ├── __init__.py
│       └── booking_service.py  # Booking create/cancel logic
├── coupons/
│   ├── __init__.py
│   ├── apps.py
│   ├── admin.py
│   ├── models.py               # Coupon, CouponUsage models
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   └── services/
│       ├── __init__.py
│       └── coupon_service.py   # Coupon validation logic
├── tests/
│   ├── __init__.py
│   ├── conftest.py             # Test fixtures
│   ├── test_events.py
│   ├── test_bookings.py
│   └── test_coupons.py
└── technical-specs/
    └── problem_requirements.md # Detailed specification
```

---

### Setup Instructions

1. **Create and activate a virtual environment:**

```bash
python -m venv venv
source venv/bin/activate        # Linux/Mac
venv\Scripts\activate           # Windows
```

2. **Install dependencies:**

```bash
pip install -r requirements.txt
```

3. **Run migrations:**

```bash
python manage.py makemigrations events bookings coupons
python manage.py migrate
```

4. **Run the tests to see failures:**

```bash
pytest tests/ -v
```

5. **Read the specification:**

Open `technical-specs/problem_requirements.md` for complete validation rules, expected exceptions, HTTP status codes, and error messages.

---

### Your Task

1. Run the tests and observe which ones fail.
2. Read the technical specification carefully.
3. Examine the source code across the project.
4. Identify and fix all the bugs — the code has missing validations, incorrect logic, and incomplete exception handling.
5. Run the tests again until **all tests pass**.

---

### Rules

- Do **not** modify the test files (`tests/`).
- Do **not** modify the models (`models.py` files).
- Do **not** modify `conftest.py`.
- Do **not** change the custom exception classes in `exceptions.py` (they are already correctly defined).
- You may modify service files, views, serializers, and any other implementation files.

---

### Evaluation

Your solution is correct when all tests pass:

```bash
pytest tests/ -v
# Expected: All tests passed ✅
```

Good luck! 🚀

