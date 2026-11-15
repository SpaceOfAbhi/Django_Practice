# Event Ticket Booking System — Technical Specification

## Business Scenario

You are a backend developer at **EventHub**, an event ticket booking platform. The platform allows users to browse events, book tickets, apply discount coupons, and manage their bookings.

A previous developer built the initial backend but left the company before completing all the validation logic and exception handling. The backend currently has partial functionality — some operations appear to work but skip critical business validations, creating potential data integrity issues and security vulnerabilities.

**Your task is to find and fix the bugs in the existing codebase so that all tests pass.**

---

## System Overview

### Django Apps

| App | Purpose |
|---|---|
| `events` | Event listing and detail retrieval |
| `bookings` | Ticket booking creation, cancellation, and management |
| `coupons` | Discount coupon validation and application |

### Key Models

- **Event**: Represents a bookable event with capacity tracking and soft deletion.
- **TicketType**: Different ticket tiers (General, VIP, etc.) linked to an event.
- **Booking**: A user's ticket reservation for an event.
- **Coupon**: Discount codes with expiry dates, usage limits, and minimum order requirements.
- **CouponUsage**: Tracks which users have used which coupons (one use per user per coupon).

---

## API Endpoints

### Events

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/events/` | List all active (non-deleted) events |
| GET | `/api/events/<id>/` | Get details of a specific event |

### Bookings

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/bookings/` | List authenticated user's bookings |
| POST | `/api/bookings/create/` | Create a new booking |
| GET | `/api/bookings/<id>/` | Get booking details |
| POST | `/api/bookings/<id>/cancel/` | Cancel a booking |

### Coupons

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/coupons/validate/` | Validate a coupon and get discount info |
| GET | `/api/coupons/<code>/` | Get coupon details |

---

## Validation Rules & Exception Specifications

### 1. Event Retrieval

#### `get_event_detail(event_id)`

| Condition | Exception | HTTP Status | Error Code | Message |
|---|---|---|---|---|
| Event does not exist | `EventNotFoundError` | 404 | `event_not_found` | "Event not found." |
| Event is soft-deleted (`is_deleted=True`) | `EventNotFoundError` | 404 | `event_not_found` | "Event not found." |

#### `list_active_events()`

- Must return only events where `is_deleted=False`.

---

### 2. Booking Creation

#### `create_booking(user, event_id, ticket_type_id, quantity, coupon_code=None)`

Validations must be performed **in this order**:

| Step | Condition | Exception | HTTP Status | Error Code | Message |
|---|---|---|---|---|---|
| 1 | Event does not exist | `EventNotFoundError` | 404 | `event_not_found` | "Event not found." |
| 2 | Event is soft-deleted | `EventNotFoundError` | 404 | `event_not_found` | "Event not found." |
| 3 | Event date is in the past | `EventExpiredError` | 400 | `event_expired` | "This event has already occurred." |
| 4 | Quantity < 1 or > 10 | `InvalidQuantityError` | 400 | `invalid_quantity` | "Quantity must be between 1 and 10." |
| 5 | Ticket type doesn't exist for this event | `EventNotFoundError` | 404 | `event_not_found` | "Ticket type not found for this event." |
| 6 | Not enough available capacity | `EventCapacityError` | 400 | `insufficient_capacity` | "Not enough tickets available." |
| 7 | User already has an active (CONFIRMED) booking for this event | `DuplicateBookingError` | 400 | `duplicate_booking` | "You already have an active booking for this event." |

#### Capacity Check Logic:
- Check `event.available_capacity >= quantity`
- The available capacity must be checked at the **event** level

#### Duplicate Booking Logic:
- A duplicate exists if the user has a `Booking` with `status="CONFIRMED"` for the same `event`
- Cancelled bookings should NOT count as duplicates

#### On Success:
- Create the booking with `status="CONFIRMED"`
- Decrease `event.available_capacity` by `quantity`
- Decrease `ticket_type.quantity_available` by `quantity`
- If a coupon is provided, validate it via `validate_and_apply_coupon()` and record the discount
- Use `transaction.atomic()` for database writes

#### Success Response (HTTP 201):
```json
{
    "success": true,
    "data": {
        "id": 1,
        "username": "testuser",
        "event_name": "Django Conference 2027",
        "ticket_type_name": "General Admission",
        "quantity": 2,
        "total_amount": "100.00",
        "discount_amount": "0.00",
        "final_amount": "100.00",
        "status": "CONFIRMED",
        "booking_date": "2026-11-15T...",
        "cancelled_at": null,
        "cancellation_reason": ""
    },
    "message": "Booking created successfully."
}
```

---

### 3. Booking Cancellation

#### `cancel_booking(user, booking_id, reason="")`

Validations must be performed **in this order**:

| Step | Condition | Exception | HTTP Status | Error Code | Message |
|---|---|---|---|---|---|
| 1 | Booking does not exist | `BookingNotFoundError` | 404 | `booking_not_found` | "Booking not found." |
| 2 | Booking does not belong to the requesting user | `BookingOwnershipError` | 403 | `booking_ownership_error` | "You do not have permission to modify this booking." |
| 3 | Booking is already cancelled (`status="CANCELLED"`) | `BookingCancellationError` | 400 | `cancellation_error` | "This booking cannot be cancelled." |
| 4 | Event starts within 24 hours | `CancellationDeadlineError` | 400 | `cancellation_deadline_passed` | "Cancellation deadline has passed. Bookings cannot be cancelled within 24 hours of the event." |

#### Cancellation Deadline Logic:
- Compare `event.event_date` with `timezone.now()`
- If the difference is **less than 24 hours**, cancellation is blocked
- The 24-hour threshold is configured via `settings.CANCELLATION_DEADLINE_HOURS`

#### On Success:
- Set booking `status` to `"CANCELLED"`
- Set `cancelled_at` to current timestamp
- Set `cancellation_reason` to the provided reason
- Restore `event.available_capacity` by `quantity`
- Restore `ticket_type.quantity_available` by `quantity`
- Use `transaction.atomic()` for database writes

#### Success Response (HTTP 200):
```json
{
    "success": true,
    "data": {
        "id": 1,
        "status": "CANCELLED",
        "cancelled_at": "2026-11-15T...",
        "cancellation_reason": "Changed plans"
    },
    "message": "Booking cancelled successfully."
}
```

---

### 4. Booking Detail Retrieval

#### `get_booking_detail(user, booking_id)`

| Condition | Exception | HTTP Status | Error Code | Message |
|---|---|---|---|---|
| Booking does not exist | `BookingNotFoundError` | 404 | `booking_not_found` | "Booking not found." |
| Booking does not belong to the requesting user | `BookingOwnershipError` | 403 | `booking_ownership_error` | "You do not have permission to modify this booking." |

---

### 5. Coupon Validation

#### `validate_and_apply_coupon(coupon_code, user, order_amount)`

Validations must be performed **in this order**:

| Step | Condition | Exception | HTTP Status | Error Code | Message |
|---|---|---|---|---|---|
| 1 | Coupon does not exist | `CouponNotFoundError` | 404 | `coupon_not_found` | "Coupon not found." |
| 2 | Coupon is soft-deleted (`is_deleted=True`) | `CouponNotFoundError` | 404 | `coupon_not_found` | "Coupon not found." |
| 3 | Coupon is inactive (`is_active=False`) | `CouponExpiredError` | 400 | `coupon_expired` | "This coupon has expired." |
| 4 | Coupon has expired (`valid_until` is in the past) | `CouponExpiredError` | 400 | `coupon_expired` | "This coupon has expired." |
| 5 | Coupon has reached maximum uses | `CouponUsageLimitError` | 400 | `coupon_usage_limit` | "This coupon has reached its maximum usage limit." |
| 6 | User has already used this coupon (entry in `CouponUsage`) | `CouponAlreadyUsedError` | 409 | `coupon_already_used` | "You have already used this coupon." |
| 7 | Order amount is below minimum (`order_amount < min_order_amount`) | `CouponMinimumAmountError` | 400 | `coupon_minimum_amount` | "Order amount does not meet the minimum requirement for this coupon." |

#### Usage Limit Logic:
- If `max_uses == 0`, the coupon has **unlimited** uses
- Otherwise, check `current_uses >= max_uses`

#### Per-User Usage Logic:
- Check if a `CouponUsage` record exists for this `coupon` and `user` combination

#### On Success:
- Calculate discount using `calculate_discount()` from `bookings.utils.pricing`
- Increment `coupon.current_uses` by 1
- **Important**: Usage count must only be incremented AFTER all validations pass. If any validation fails, usage count must NOT change.

---

## Custom Exception Classes

All custom exceptions are defined in `eventbooking/exceptions.py` and extend `rest_framework.exceptions.APIException`.

| Exception Class | HTTP Status | Error Code |
|---|---|---|
| `EventNotFoundError` | 404 | `event_not_found` |
| `BookingNotFoundError` | 404 | `booking_not_found` |
| `CouponNotFoundError` | 404 | `coupon_not_found` |
| `EventCapacityError` | 400 | `insufficient_capacity` |
| `EventExpiredError` | 400 | `event_expired` |
| `DuplicateBookingError` | 400 | `duplicate_booking` |
| `BookingOwnershipError` | 403 | `booking_ownership_error` |
| `BookingCancellationError` | 400 | `cancellation_error` |
| `CancellationDeadlineError` | 400 | `cancellation_deadline_passed` |
| `CouponExpiredError` | 400 | `coupon_expired` |
| `CouponUsageLimitError` | 400 | `coupon_usage_limit` |
| `CouponMinimumAmountError` | 400 | `coupon_minimum_amount` |
| `CouponAlreadyUsedError` | 409 | `coupon_already_used` |
| `InvalidQuantityError` | 400 | `invalid_quantity` |

---

## Error Response Format

All API errors must follow this structure:

```json
{
    "success": false,
    "error": {
        "code": "<error_code>",
        "message": "<error_message>"
    }
}
```

This is handled by the custom exception handler in `eventbooking/exceptions.py`.

---

## Database Constraints

- `CouponUsage` has a `unique_together` constraint on `(coupon, user)` — each user can use each coupon at most once.
- `TicketType` has a `unique_together` constraint on `(event, name)` — ticket type names are unique per event.
- All monetary amounts use `DecimalField(max_digits=10, decimal_places=2)`.

---

## Edge Cases to Consider

1. **Booking for a soft-deleted event**: Must return 404, not allow booking.
2. **Booking for a past event**: Must return 400, not allow booking.
3. **Booking with quantity 0 or negative**: Must return 400.
4. **Booking with quantity > 10**: Must return 400 (business rule: max 10 tickets per booking).
5. **Second booking for same event by same user**: Must return 400 (duplicate).
6. **Cancelled booking then re-booking**: Should allow re-booking since previous booking was cancelled.
7. **Cancelling another user's booking**: Must return 403.
8. **Cancelling an already cancelled booking**: Must return 400.
9. **Cancelling within 24 hours of event**: Must return 400.
10. **Using a soft-deleted coupon**: Must return 404.
11. **Using an expired coupon**: Must return 400.
12. **Using an inactive coupon**: Must return 400.
13. **Using a coupon at its usage limit**: Must return 400.
14. **Using a coupon already used by this user**: Must return 409.
15. **Using a coupon with order below minimum**: Must return 400.
16. **Failed validations must not change any database state** (no capacity changes, no usage increments).
17. **Viewing another user's booking**: Must return 403.

---

## Testing

Run all tests with:

```bash
pytest tests/ -v
```

Run specific test files:

```bash
pytest tests/test_events.py -v
pytest tests/test_bookings.py -v
pytest tests/test_coupons.py -v
```

The tests validate all the rules described above. Your implementation is correct when **all tests pass**.

