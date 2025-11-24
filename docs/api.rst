API Reference
=============

This section provides a complete overview of all API endpoints across all services. For detailed documentation of each service, see the individual service documentation pages.

Users Service API
-----------------

**Base URL:** ``http://localhost:8001``  
**Main File:** ``users_service/app/routers/users.py``

Complete documentation: :doc:`users_service`

Quick Reference:
   * POST /users/register - Register new user
   * POST /users/login - Authenticate and get token
   * GET /users/ - Get all users (Admin only)
   * GET /users/{username} - Get user by username
   * PUT /users/{username} - Update user profile
   * PUT /users/{username}/role - Update user role (Admin only)
   * PUT /users/{username}/activate - Activate user (Admin only)
   * PUT /users/{username}/deactivate - Deactivate user (Admin only)
   * DELETE /users/{username} - Delete user (Admin only)
   * GET /users/{username}/history - Get booking history

Rooms Service API
-----------------

**Base URL:** ``http://localhost:8002``  
**Main File:** ``rooms_service/app/routers/rooms.py``

Complete documentation: :doc:`rooms_service`

Quick Reference:
   * POST /rooms/add - Add new room (Admin only)
   * GET /rooms/ - Get all rooms
   * GET /rooms/{room_id} - Get room by ID
   * GET /rooms/available - Get available rooms with filters
   * GET /rooms/status/{room_id} - Get room availability status
   * PUT /rooms/update/{room_id} - Update room (Admin only)
   * DELETE /rooms/delete/{room_id} - Delete room (Admin only)

Bookings Service API
--------------------

**Base URL:** ``http://localhost:8003``  
**Main File:** ``bookings_service/app/routers/bookings.py``

Complete documentation: :doc:`bookings_service`

Quick Reference:
   * POST /bookings/create - Create new booking
   * GET /bookings/ - Get all bookings (Admin only)
   * GET /bookings/{booking_id} - Get booking by ID
   * GET /bookings/user/{username} - Get user's bookings
   * GET /bookings/check - Check room availability
   * PUT /bookings/{booking_id} - Update booking
   * DELETE /bookings/{booking_id} - Delete booking

Reviews Service API
-------------------

**Base URL:** ``http://localhost:8004``  
**Main File:** ``reviews_service/app/routers/reviews.py``

Complete documentation: :doc:`reviews_service`

Quick Reference:
   * POST /reviews/create - Submit review
   * GET /reviews/ - Get all reviews (Admin only)
   * GET /reviews/{review_id} - Get review by ID
   * GET /reviews/room/{room_id} - Get reviews for room
   * GET /reviews/user/{username} - Get reviews by user
   * PUT /reviews/{review_id} - Update review
   * POST /reviews/{review_id}/flag - Flag review
   * POST /reviews/{review_id}/unflag - Unflag review (Moderator/Admin)
   * GET /reviews/flagged/all - Get flagged reviews (Moderator/Admin)
   * DELETE /reviews/{review_id} - Delete review

