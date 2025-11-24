Rooms Service API Documentation
=================================

This module contains all the API endpoints for managing meeting rooms, their availability, and room-related operations.

**File Location:** ``rooms_service/app/routers/rooms.py``

Module Contents
----------------

.. automodule:: rooms_service.app.routers.rooms
   :members:
   :undoc-members:
   :show-inheritance:

Helper Functions
----------------

sanitize_string
~~~~~~~~~~~~~~~

.. autofunction:: rooms_service.app.routers.rooms.sanitize_string

**File:** ``rooms_service/app/routers/rooms.py``

**Description:**
   This function sanitizes string inputs to prevent SQL injection and XSS attacks. It removes dangerous 
   characters before storing room names, equipment descriptions, and locations in the database.

API Endpoints
-------------

POST /rooms/add
~~~~~~~~~~~~~~~

.. autofunction:: rooms_service.app.routers.rooms.add_room

**File:** ``rooms_service/app/routers/rooms.py``

**Description:**
   Creates a new meeting room in the system. The room is automatically set as available when created. 
   Room names must be unique. This endpoint validates that the capacity is greater than zero and that 
   no room with the same name already exists.

**Request Body:**
   - name (string, required): Name of the room (must be unique)
   - capacity (integer, required): Maximum number of people (must be > 0)
   - equipment (string, optional): Description of available equipment
   - location (string, optional): Physical location of the room

**Access Control:** Admin role required

**Response:** 201 Created with room details including ID and is_available status

GET /rooms/
~~~~~~~~~~~

.. autofunction:: rooms_service.app.routers.rooms.get_all_rooms

**File:** ``rooms_service/app/routers/rooms.py``

**Description:**
   Retrieves a list of all rooms in the system, regardless of availability status. This is useful for 
   getting an overview of all meeting spaces.

**Access Control:** All authenticated users (regular_user, moderator, admin)

**Response:** 200 OK with list of all rooms

GET /rooms/{room_id}
~~~~~~~~~~~~~~~~~~~~

.. autofunction:: rooms_service.app.routers.rooms.get_room

**File:** ``rooms_service/app/routers/rooms.py``

**Description:**
   Gets detailed information about a specific room by its ID. This includes capacity, equipment, location, 
   and availability status.

**URL Parameters:**
   - room_id (integer, required): ID of the room

**Access Control:** All authenticated users

**Response:** 200 OK with room details

GET /rooms/available
~~~~~~~~~~~~~~~~~~~~

.. autofunction:: rooms_service.app.routers.rooms.get_available_rooms

**File:** ``rooms_service/app/routers/rooms.py``

**Description:**
   Retrieves only the rooms that are currently available. This endpoint supports filtering by capacity, 
   location, and equipment. All filters are optional and can be combined. The location and equipment 
   filters use partial matching (contains), so you can search for "Building A" and it will find rooms 
   in "Building A, Floor 2".

**Query Parameters (all optional):**
   - capacity (integer): Minimum capacity required
   - location (string): Filter by location (partial match)
   - equipment (string): Filter by equipment (partial match)

**Example:** ``/rooms/available?capacity=10&location=Building A&equipment=Projector``

**Access Control:** All authenticated users

**Response:** 200 OK with list of available rooms matching the filters

GET /rooms/status/{room_id}
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autofunction:: rooms_service.app.routers.rooms.get_room_status

**File:** ``rooms_service/app/routers/rooms.py``

**Description:**
   Quickly checks if a specific room is available or not. This is useful before attempting to make a booking. 
   Returns just the room ID and availability status.

**URL Parameters:**
   - room_id (integer, required): ID of the room

**Access Control:** All authenticated users

**Response:** 200 OK with room_id and is_available boolean

PUT /rooms/update/{room_id}
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autofunction:: rooms_service.app.routers.rooms.update_room

**File:** ``rooms_service/app/routers/rooms.py``

**Description:**
   Updates room details. All fields are optional - only the fields you provide will be updated. 
   This is useful for changing capacity, updating equipment lists, or marking rooms as unavailable 
   (for maintenance, for example). The endpoint validates that room names remain unique and that 
   capacity is always greater than zero.

**URL Parameters:**
   - room_id (integer, required): ID of the room to update

**Request Body (all optional):**
   - name (string): New room name
   - capacity (integer): New capacity (must be > 0)
   - equipment (string): New equipment description
   - location (string): New location
   - is_available (boolean): Set availability status

**Access Control:** Admin role required

**Response:** 200 OK with updated room details

DELETE /rooms/delete/{room_id}
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autofunction:: rooms_service.app.routers.rooms.delete_room

**File:** ``rooms_service/app/routers/rooms.py``

**Description:**
   Permanently deletes a room from the system. This action cannot be undone. Be careful when deleting 
   rooms that have existing bookings or reviews.

**URL Parameters:**
   - room_id (integer, required): ID of the room to delete

**Access Control:** Admin role required

**Response:** 200 OK with success message

