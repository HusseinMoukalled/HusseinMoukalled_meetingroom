Authentication
==============

The system uses JWT (JSON Web Tokens) for authentication.

Getting an Access Token
-----------------------

To authenticate, send a POST request to ``/users/login`` with username and password:

.. code-block:: json

   {
     "username": "user1",
     "password": "password123"
   }

Response:

.. code-block:: json

   {
     "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
     "token_type": "bearer"
   }

Using the Access Token
----------------------

Include the token in the Authorization header for all protected endpoints:

.. code-block:: http

   Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

Token Expiration
----------------

Access tokens expire after 60 minutes. Users need to log in again to get a new token.

Role-Based Access Control
-------------------------

The system supports three roles:

* **Admin**: Full access to all services
* **Moderator**: Can moderate reviews, view flagged content
* **Regular User**: Can manage own bookings and reviews

Each endpoint enforces role-based permissions.

