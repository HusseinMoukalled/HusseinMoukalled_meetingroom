Bookings Service API Documentation
===================================

This module contains all the API endpoints for managing meeting room bookings, checking availability, and handling booking conflicts.

**File Location:** ``bookings_service/app/routers/bookings.py``

Module Contents
----------------

.. automodule:: bookings_service.app.routers.bookings
   :members:
   :undoc-members:
   :show-inheritance:

Helper Functions
----------------

sanitize_string
~~~~~~~~~~~~~~~

.. autofunction:: bookings_service.app.routers.bookings.sanitize_string

**File:** ``bookings_service/app/routers/bookings.py``

**Description:**
   Sanitizes string inputs to prevent SQL injection attacks. Used when storing usernames in bookings.

API Endpoints
-------------

POST /bookings/create
~~~~~~~~~~~~~~~~~~~~~

.. autofunction:: bookings_service.app.routers.bookings.create_booking

**File:** ``bookings_service/app/routers/bookings.py``

**Description:**
   Creates a new booking for a meeting room. This endpoint performs several important validations:
   
   1. Checks that the user exists
   2. Checks that the room exists and is available
   3. Validates that end_time is after start_time
   4. Prevents overlapping bookings (same room, same date, overlapping times)
   5. Ensures regular users can only book for themselves
   
   The overlap detection is smart - it checks if the new booking's time range overlaps with any existing 
   booking for the same room on the same date.

**Request Body:**
   - username (string, required): Username of the person making the booking
   - room_id (integer, required): ID of the room to book
   - date (date, required): Booking date in format YYYY-MM-DD
   - start_time (time, required): Start time in format HH:MM:SS
   - end_time (time, required): End time in format HH:MM:SS

**Access Control:**
   - Regular users: Can only book for themselves
   - Admin: Can book for any user

**Response:** 201 Created with booking details including ID

GET /bookings/
~~~~~~~~~~~~~~

.. autofunction:: bookings_service.app.routers.bookings.get_all_bookings

**File:** ``bookings_service/app/routers/bookings.py``

**Description:**
   Retrieves a list of all bookings in the system. This is useful for administrators to see the overall 
   booking activity and manage conflicts.

**Access Control:** Admin role required

**Response:** 200 OK with list of all bookings

GET /bookings/{booking_id}
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autofunction:: bookings_service.app.routers.bookings.get_booking

**File:** ``bookings_service/app/routers/bookings.py``

**Description:**
   Gets detailed information about a specific booking by its ID. Regular users can only view their own 
   bookings, while admins can view any booking.

**URL Parameters:**
   - booking_id (integer, required): ID of the booking

**Access Control:**
   - Regular users: Can only view own bookings
   - Admin: Can view any booking

**Response:** 200 OK with booking details

GET /bookings/user/{username}
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autofunction:: bookings_service.app.routers.bookings.get_user_bookings

**File:** ``bookings_service/app/routers/bookings.py``

**Description:**
   Retrieves all bookings for a specific user. This is useful for users to see their booking history, 
   or for admins to check a user's bookings.

**URL Parameters:**
   - username (string, required): Username of the user

**Access Control:**
   - Regular users: Can only view own bookings
   - Admin: Can view any user's bookings

**Response:** 200 OK with list of bookings for that user

GET /bookings/check
~~~~~~~~~~~~~~~~~~~

.. autofunction:: bookings_service.app.routers.bookings.check_room_availability

**File:** ``bookings_service/app/routers/bookings.py``

**Description:**
   Checks if a room is available for a specific time slot without actually creating a booking. This is 
   useful for users to check availability before attempting to book. The endpoint checks:
   
   1. That the room exists
   2. That the room is marked as available
   3. That there are no conflicting bookings for that time slot
   
   Returns a simple boolean indicating availability.

**Query Parameters:**
   - room_id (integer, required): ID of the room
   - date (date, required): Date in format YYYY-MM-DD
   - start_time (time, required): Start time in format HH:MM:SS
   - end_time (time, required): End time in format HH:MM:SS

**Example:** ``/bookings/check?room_id=1&date=2025-12-31&start_time=10:00:00&end_time=11:00:00``

**Access Control:** All authenticated users

**Response:** 200 OK with {"available": true/false}

PUT /bookings/{booking_id}
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autofunction:: bookings_service.app.routers.bookings.update_booking

**File:** ``bookings_service/app/routers/bookings.py``

**Description:**
   Updates an existing booking. You can change the date, start time, or end time. All fields are optional. 
   The endpoint performs the same validations as create_booking:
   
   1. Validates time range (end_time after start_time)
   2. Checks for overlapping bookings after the update
   3. Ensures users can only update their own bookings
   
   This is useful for rescheduling bookings.

**URL Parameters:**
   - booking_id (integer, required): ID of the booking to update

**Request Body (all optional):**
   - date (date): New booking date
   - start_time (time): New start time
   - end_time (time): New end time

**Access Control:**
   - Regular users: Can only update own bookings
   - Admin: Can update any booking

**Response:** 200 OK with updated booking details

DELETE /bookings/{booking_id}
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autofunction:: bookings_service.app.routers.bookings.delete_booking

**File:** ``bookings_service/app/routers/bookings.py``

**Description:**
   Cancels/deletes a booking. This permanently removes the booking from the system. Regular users can 
   only delete their own bookings, while admins can delete any booking (useful for resolving conflicts 
   or handling cancellations).

**URL Parameters:**
   - booking_id (integer, required): ID of the booking to delete

**Access Control:**
   - Regular users: Can only delete own bookings
   - Admin: Can delete any booking

**Response:** 200 OK with success message

