Users Service API Documentation
==================================

This module contains all the API endpoints for user management, authentication, and authorization.

**File Location:** ``users_service/app/routers/users.py``

Module Contents
----------------

.. automodule:: users_service.app.routers.users
   :members:
   :undoc-members:
   :show-inheritance:

Helper Functions
----------------

sanitize_string
~~~~~~~~~~~~~~~

.. autofunction:: users_service.app.routers.users.sanitize_string

This function is used throughout the users service to clean user input and prevent SQL injection attacks. 
It removes dangerous characters like semicolons, quotes, and backslashes that could be used maliciously.

**Location:** ``users_service/app/routers/users.py``

**Example Usage:**
   When a user registers, their username and name are sanitized before being stored in the database.

validate_password
~~~~~~~~~~~~~~~~~

.. autofunction:: users_service.app.routers.users.validate_password

Checks if a password meets the minimum security requirements (at least 6 characters).

**Location:** ``users_service/app/routers/users.py``

validate_role
~~~~~~~~~~~~~

.. autofunction:: users_service.app.routers.users.validate_role

Ensures that only valid roles (regular_user, admin, moderator) can be assigned to users.

**Location:** ``users_service/app/routers/users.py``

API Endpoints
-------------

POST /users/register
~~~~~~~~~~~~~~~~~~~~

.. autofunction:: users_service.app.routers.users.register_user

**File:** ``users_service/app/routers/users.py``

**Description:**
   This endpoint allows anyone to create a new user account. The password is automatically hashed using bcrypt 
   before storage. Regular users can only create accounts with the "regular_user" role, while admins can create 
   accounts with any role.

**Request Body:**
   - name (string, required): Full name of the user
   - username (string, required): Unique username, minimum 3 characters
   - email (string, required): Valid email address, must be unique
   - password (string, required): Password, minimum 6 characters
   - role (string, optional): User role, defaults to "regular_user"

**Response:** 201 Created with user details (password is not included)

POST /users/login
~~~~~~~~~~~~~~~~~

.. autofunction:: users_service.app.routers.users.login

**File:** ``users_service.app.routers.users.py``

**Description:**
   Authenticates a user and returns a JWT token that can be used for subsequent API requests. 
   The token expires after 60 minutes. Inactive users cannot login.

**Request Body:**
   - username (string, required): Username
   - password (string, required): User password

**Response:** 200 OK with access_token and token_type

GET /users/
~~~~~~~~~~~

.. autofunction:: users_service.app.routers.users.get_all_users

**File:** ``users_service/app/routers/users.py``

**Description:**
   Retrieves a list of all users in the system. This is an admin-only endpoint for security reasons.

**Access Control:** Admin role required

**Response:** 200 OK with list of all users

GET /users/{username}
~~~~~~~~~~~~~~~~~~~~~~

.. autofunction:: users_service.app.routers.users.get_user

**File:** ``users_service/app/routers/users.py``

**Description:**
   Gets detailed information about a specific user. Regular users can only view their own profile, 
   while admins can view any user's profile.

**URL Parameters:**
   - username (string, required): Username of the user to retrieve

**Access Control:** 
   - Regular users: Can only view own profile
   - Admin: Can view any profile

**Response:** 200 OK with user details

PUT /users/{username}
~~~~~~~~~~~~~~~~~~~~~

.. autofunction:: users_service.app.routers.users.update_user

**File:** ``users_service/app/routers/users.py``

**Description:**
   Updates user profile information. Users can update their name, email, or password. 
   All fields are optional - only provided fields will be updated.

**URL Parameters:**
   - username (string, required): Username of the user to update

**Request Body (all optional):**
   - name (string): New full name
   - email (string): New email address
   - password (string): New password

**Access Control:**
   - Regular users: Can only update own profile
   - Admin: Can update any profile

**Response:** 200 OK with updated user details

PUT /users/{username}/role
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autofunction:: users_service.app.routers.users.update_user_role

**File:** ``users_service/app/routers/users.py``

**Description:**
   Changes a user's role. This is useful for promoting users to admin or moderator, or demoting them.

**URL Parameters:**
   - username (string, required): Username of the user

**Query Parameters:**
   - new_role (string, required): New role (regular_user, admin, or moderator)

**Access Control:** Admin role required

**Response:** 200 OK with updated user details

PUT /users/{username}/activate
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autofunction:: users_service.app.routers.users.activate_user

**File:** ``users_service/app/routers/users.py``

**Description:**
   Reactivates a user account that was previously deactivated. Once activated, the user can login again.

**URL Parameters:**
   - username (string, required): Username of the user

**Access Control:** Admin role required

**Response:** 200 OK with user details

PUT /users/{username}/deactivate
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autofunction:: users_service.app.routers.users.deactivate_user

**File:** ``users_service/app/routers/users.py``

**Description:**
   Deactivates a user account. Deactivated users cannot login until reactivated by an admin.

**URL Parameters:**
   - username (string, required): Username of the user

**Access Control:** Admin role required

**Response:** 200 OK with user details

DELETE /users/{username}
~~~~~~~~~~~~~~~~~~~~~~~~

.. autofunction:: users_service.app.routers.users.delete_user

**File:** ``users_service/app/routers/users.py``

**Description:**
   Permanently deletes a user account from the system. This action cannot be undone.

**URL Parameters:**
   - username (string, required): Username of the user to delete

**Access Control:** Admin role required

**Response:** 200 OK with success message

GET /users/{username}/history
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autofunction:: users_service.app.routers.users.booking_history

**File:** ``users_service/app/routers/users.py``

**Description:**
   Retrieves the complete booking history for a specific user. The bookings are ordered by date 
   and time (most recent first). This uses a parameterized SQL query to prevent SQL injection.

**URL Parameters:**
   - username (string, required): Username of the user

**Access Control:**
   - Regular users: Can only view own history
   - Admin: Can view any user's history

**Response:** 200 OK with username and list of bookings

Authentication Module
---------------------

.. automodule:: users_service.app.auth
   :members:
   :undoc-members:

**File Location:** ``users_service/app/auth.py``

hash_password
~~~~~~~~~~~~~

.. autofunction:: users_service.app.auth.hash_password

**File:** ``users_service/app/auth.py``

**Description:**
   Hashes a password using bcrypt with 12 rounds. This is a one-way function - the original password 
   cannot be recovered from the hash. We use bcrypt directly instead of passlib to avoid initialization issues.

verify_password
~~~~~~~~~~~~~~~

.. autofunction:: users_service.app.auth.verify_password

**File:** ``users_service/app/auth.py``

**Description:**
   Verifies if a plain text password matches a hashed password. Returns True if they match, False otherwise.

create_access_token
~~~~~~~~~~~~~~~~~~~

.. autofunction:: users_service.app.auth.create_access_token

**File:** ``users_service/app/auth.py``

**Description:**
   Creates a JWT (JSON Web Token) that contains the username and expiration time. The token is valid for 60 minutes.

decode_token
~~~~~~~~~~~~

.. autofunction:: users_service.app.auth.decode_token

**File:** ``users_service/app/auth.py``

**Description:**
   Decodes a JWT token and extracts the user information. Raises an exception if the token is invalid or expired.

Dependencies Module
-------------------

.. automodule:: users_service.app.deps
   :members:
   :undoc-members:

**File Location:** ``users_service/app/deps.py``

get_current_user
~~~~~~~~~~~~~~~~

.. autofunction:: users_service.app.deps.get_current_user

**File:** ``users_service/app/deps.py``

**Description:**
   This is a FastAPI dependency that extracts the JWT token from the Authorization header, decodes it, 
   and retrieves the user from the database. It's used by almost all protected endpoints.

require_admin
~~~~~~~~~~~~~

.. autofunction:: users_service.app.deps.require_admin

**File:** ``users_service/app/deps.py``

**Description:**
   A dependency that ensures only admin users can access an endpoint. If a non-admin tries to access, 
   they get a 403 Forbidden error.

require_moderator
~~~~~~~~~~~~~~~~~

.. autofunction:: users_service.app.deps.require_moderator

**File:** ``users_service/app/deps.py``

**Description:**
   A dependency that ensures only moderators or admins can access an endpoint. Regular users get a 403 error.

require_regular_user_or_above
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autofunction:: users_service.app.deps.require_regular_user_or_above

**File:** ``users_service/app/deps.py``

**Description:**
   A dependency that ensures the user is at least a regular user (regular_user, moderator, or admin). 
   This is used for endpoints that require authentication but don't need special permissions.

