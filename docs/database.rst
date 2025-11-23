Database Schema
================

The system uses PostgreSQL as the database.

Tables
------

Users Table
~~~~~~~~~~~

.. code-block:: sql

   CREATE TABLE users (
       id SERIAL PRIMARY KEY,
       name VARCHAR NOT NULL,
       username VARCHAR UNIQUE NOT NULL,
       email VARCHAR UNIQUE NOT NULL,
       hashed_password VARCHAR NOT NULL,
       role VARCHAR DEFAULT 'regular_user',
       is_active BOOLEAN DEFAULT TRUE
   );

Rooms Table
~~~~~~~~~~~

.. code-block:: sql

   CREATE TABLE rooms (
       id SERIAL PRIMARY KEY,
       name VARCHAR NOT NULL,
       capacity INTEGER NOT NULL,
       equipment VARCHAR,
       location VARCHAR,
       is_available BOOLEAN DEFAULT TRUE
   );

Bookings Table
~~~~~~~~~~~~~~

.. code-block:: sql

   CREATE TABLE bookings (
       id SERIAL PRIMARY KEY,
       username VARCHAR NOT NULL,
       room_id INTEGER NOT NULL,
       date DATE NOT NULL,
       start_time TIME NOT NULL,
       end_time TIME NOT NULL
   );

Reviews Table
~~~~~~~~~~~~~

.. code-block:: sql

   CREATE TABLE reviews (
       id SERIAL PRIMARY KEY,
       username VARCHAR NOT NULL,
       room_id INTEGER NOT NULL,
       rating INTEGER NOT NULL,
       comment VARCHAR,
       is_flagged BOOLEAN DEFAULT FALSE,
       flag_reason VARCHAR
   );

Relationships
-------------

* Reviews reference Users (username) and Rooms (room_id)
* Bookings reference Users (username) and Rooms (room_id)

