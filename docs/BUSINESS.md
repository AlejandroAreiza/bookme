# BookMe: Business Purpose

> Find local experiences and secure your spot in seconds.

## Mission

BookMe helps people **find local experiences and secure their spot in seconds**, and helps small organizers **fill their events without overselling**.

## The problem

### For attendees

- What's happening nearby is scattered across Instagram, WhatsApp groups, flyers and word of mouth.
- Reserving a spot often means messaging someone and hoping there's still room.
- There's no single place to see "my upcoming plans".

### For small organizers

Yoga teachers, small venues, meetup hosts, workshop leaders.

- Sign-ups are tracked by hand in spreadsheets, DMs or paper lists.
- Events end up **overbooked** (angry guests) or **half empty** (lost income).
- Collecting payments and chasing no-shows takes time away from running the event.

## The solution

One simple platform where:

- **Attendees** discover local experiences, see how many spots are left, and book in a couple of clicks.
- **Organizers** publish events, set the capacity, and see who's coming.
- **The system guarantees each spot is sold only once**, even when many people book at the same moment.

## Who uses it

| User | Goals | What they do in BookMe |
| --- | --- | --- |
| **Attendee** | Find something fun nearby and be sure they're in | Browse events, book a spot, pay now or later, see their bookings |
| **Organizer** | Fill the event without overselling, with less admin | Create and edit events, set capacity, see attendees |

## What kind of experiences

Anything local with a **limited number of spots**:

- Concerts and live music
- Theater, stand-up comedy, cinema screenings
- Sports matches
- Tech meetups, workshops, conferences
- Yoga, fitness, cooking and art classes
- Exhibitions and guided tours

## Value proposition

- **Local first:** focused on community and small-scale experiences, not stadium tours.
- **Your spot is guaranteed:** no double-booking, ever.
- **Fast:** from discovering an event to holding a spot in seconds.
- **Flexible payment** (planned): pay now, or hold the spot and pay later before a deadline.

## Business model (real-world version)

BookMe is a learning project, but if it were a real product it could earn money through:

- **Booking fee:** a small percentage (e.g. 3–5%) of each paid booking.
- **Organizer plan:** a monthly subscription with extra features (analytics, custom branding, waitlists).
- Free events stay free to publish, which helps grow the catalog.

## Key booking rules

1. An event has a fixed **capacity**. Available spots = capacity − booked spots.
2. A spot can belong to **only one** booking.
3. When an event has 0 available spots, it is **sold out** and new bookings are rejected.
4. *(Planned)* **Pay later:** a spot is **held** (`PENDING`) until a payment deadline. If it isn't paid in time, the hold expires and the spot goes back on sale.
5. *(Planned)* **Pay now:** the payment is approved and the booking becomes `CONFIRMED` immediately.

## Success metrics (if it were real)

- **Fill rate:** % of event capacity that gets booked.
- **Time to book:** seconds from opening an event to securing a spot.
- **Oversold bookings:** must always be **0**.
- **Repeat attendees:** % of users who book a second event.

## Scope

| Version | Includes |
| --- | --- |
| **v1 (learning challenges)** | Browse events, manage events (CRUD), book a spot, no double-booking. No payment. |
| **Next** | Mock payments, pay now or later, expiring holds, user accounts (login), notifications |
| **Later** | Real payments (Stripe test mode), organizer dashboard, waitlists, search by location |
