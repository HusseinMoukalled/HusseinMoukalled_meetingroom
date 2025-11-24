Services Overview
=================

Hussein's Meeting Room Management System consists of four microservices:

Users Service
-------------

The Users Service handles user management, authentication, and authorization.

**Location:** ``users_service/``

**Port:** 8001

**Key Features:**
* User registration and login
* JWT token-based authentication
* Role-based access control (Admin, Regular User, Moderator)
* User profile management
* Booking history tracking

**Main Components:**
* ``app/main.py`` - FastAPI application
* ``app/routers/users.py`` - User endpoints
* ``app/auth.py`` - Authentication utilities
* ``app/deps.py`` - Dependency injection for authentication
* ``app/models.py`` - User database model
* ``app/schemas.py`` - Pydantic schemas

Rooms Service
------------

The Rooms Service manages meeting room information and availability.

**Location:** ``rooms_service/``

**Port:** 8002

**Key Features:**
* Add, update, and delete rooms
* Room availability management
* Search and filter rooms
* Room status checking

**Main Components:**
* ``app/main.py`` - FastAPI application
* ``app/routers/rooms.py`` - Room endpoints
* ``app/models.py`` - Room database model
* ``app/schemas.py`` - Pydantic schemas

Bookings Service
---------------

The Bookings Service handles meeting room reservations.

**Location:** ``bookings_service/``

**Port:** 8003

**Key Features:**
* Create, update, and cancel bookings
* Room availability checking
* Booking conflict prevention
* Booking history per user

**Main Components:**
* ``app/main.py`` - FastAPI application
* ``app/routers/bookings.py`` - Booking endpoints
* ``app/models.py`` - Booking database model
* ``app/schemas.py`` - Pydantic schemas

Reviews Service
--------------

The Reviews Service manages room reviews and ratings with moderation capabilities.

**Location:** ``reviews_service/``

**Port:** 8004

**Key Features:**
* Submit and update reviews
* Rating system (1-5 stars)
* Review moderation (flagging inappropriate reviews)
* View reviews by room or user

**Main Components:**
* ``app/main.py`` - FastAPI application
* ``app/routers/reviews.py`` - Review endpoints
* ``app/models.py`` - Review database model
* ``app/schemas.py`` - Pydantic schemas

