Reviews Service API Documentation
===================================

This module contains all the API endpoints for managing room reviews, ratings, and moderation features.

**File Location:** ``reviews_service/app/routers/reviews.py``

Module Contents
----------------

.. automodule:: reviews_service.app.routers.reviews
   :members:
   :undoc-members:
   :show-inheritance:

Helper Functions
----------------

sanitize_string
~~~~~~~~~~~~~~~

.. autofunction:: reviews_service.app.routers.reviews.sanitize_string

**File:** ``reviews_service/app/routers/reviews.py``

**Description:**
   Sanitizes string inputs to prevent SQL injection and XSS attacks. Used for review comments to ensure 
   malicious code cannot be injected into the database or displayed to users.

validate_rating
~~~~~~~~~~~~~~~~

.. autofunction:: reviews_service.app.routers.reviews.validate_rating

**File:** ``reviews_service/app/routers/reviews.py``

**Description:**
   Validates that a rating is between 1 and 5. This ensures all reviews use a consistent rating scale.

API Endpoints
-------------

POST /reviews/create
~~~~~~~~~~~~~~~~~~~~~

.. autofunction:: reviews_service.app.routers.reviews.create_review

**File:** ``reviews_service/app/routers/reviews.py``

**Description:**
   Submits a review for a meeting room. Each user can only submit one review per room - if they try to 
   submit another, they'll get an error telling them to update their existing review instead. The endpoint 
   validates:
   
   1. Rating is between 1 and 5
   2. User exists
   3. Room exists
   4. User hasn't already reviewed this room
   5. Regular users can only review for themselves
   
   The comment is automatically sanitized to prevent XSS attacks.

**Request Body:**
   - username (string, required): Username of the reviewer
   - room_id (integer, required): ID of the room being reviewed
   - rating (integer, required): Rating from 1 to 5
   - comment (string, required): Review comment text

**Access Control:**
   - Regular users: Can only submit reviews for themselves
   - Admin: Can submit reviews for any user

**Response:** 201 Created with review details

GET /reviews/
~~~~~~~~~~~~~

.. autofunction:: reviews_service.app.routers.reviews.get_all_reviews

**File:** ``reviews_service/app/routers/reviews.py``

**Description:**
   Retrieves a list of all reviews in the system. This is useful for administrators to monitor all 
   reviews and identify issues.

**Access Control:** Admin role required

**Response:** 200 OK with list of all reviews

GET /reviews/{review_id}
~~~~~~~~~~~~~~~~~~~~~~~~~

.. autofunction:: reviews_service.app.routers.reviews.get_review

**File:** ``reviews_service/app/routers/reviews.py``

**Description:**
   Gets detailed information about a specific review by its ID. This includes the rating, comment, 
   and moderation status (flagged or not).

**URL Parameters:**
   - review_id (integer, required): ID of the review

**Access Control:** All authenticated users

**Response:** 200 OK with review details

GET /reviews/room/{room_id}
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autofunction:: reviews_service.app.routers.reviews.get_reviews_for_room

**File:** ``reviews_service/app/routers/reviews.py``

**Description:**
   Retrieves all reviews for a specific room. This is useful for users to see what others think about 
   a room before booking it. The endpoint validates that the room exists before returning reviews.

**URL Parameters:**
   - room_id (integer, required): ID of the room

**Access Control:** All authenticated users

**Response:** 200 OK with list of reviews for that room

GET /reviews/user/{username}
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autofunction:: reviews_service.app.routers.reviews.get_reviews_by_user

**File:** ``reviews_service/app/routers/reviews.py``

**Description:**
   Retrieves all reviews submitted by a specific user. Regular users can only view their own reviews, 
   while admins can view any user's reviews.

**URL Parameters:**
   - username (string, required): Username of the reviewer

**Access Control:**
   - Regular users: Can only view own reviews
   - Admin: Can view any user's reviews

**Response:** 200 OK with list of reviews by that user

PUT /reviews/{review_id}
~~~~~~~~~~~~~~~~~~~~~~~~~

.. autofunction:: reviews_service.app.routers.reviews.update_review

**File:** ``reviews_service/app/routers/reviews.py``

**Description:**
   Updates an existing review. Users can change their rating or comment. Both fields are optional. 
   The rating is validated to ensure it's still between 1 and 5, and the comment is sanitized.

**URL Parameters:**
   - review_id (integer, required): ID of the review to update

**Request Body (all optional):**
   - rating (integer): New rating (1-5)
   - comment (string): New comment text

**Access Control:**
   - Regular users: Can only update own reviews
   - Admin: Can update any review

**Response:** 200 OK with updated review details

POST /reviews/{review_id}/flag
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autofunction:: reviews_service.app.routers.reviews.flag_review

**File:** ``reviews_service/app/routers/reviews.py``

**Description:**
   Flags a review as inappropriate. This is the first step in the moderation process. Any authenticated 
   user can flag a review if they think it contains inappropriate content. The review is marked as 
   flagged and the reason is stored for moderators to review later.

**URL Parameters:**
   - review_id (integer, required): ID of the review to flag

**Request Body:**
   - reason (string, required): Reason for flagging the review

**Access Control:** All authenticated users

**Response:** 200 OK with review details (is_flagged will be true)

POST /reviews/{review_id}/unflag
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autofunction:: reviews_service.app.routers.reviews.unflag_review

**File:** ``reviews_service/app/routers/reviews.py``

**Description:**
   Removes the flag from a review. This is used by moderators or admins when they determine that a 
   flagged review is actually appropriate. The flag_reason is cleared and is_flagged is set to false.

**URL Parameters:**
   - review_id (integer, required): ID of the review to unflag

**Access Control:** Moderator or Admin role required

**Response:** 200 OK with review details (is_flagged will be false)

GET /reviews/flagged/all
~~~~~~~~~~~~~~~~~~~~~~~~~

.. autofunction:: reviews_service.app.routers.reviews.get_flagged_reviews

**File:** ``reviews_service/app/routers/reviews.py``

**Description:**
   Retrieves all reviews that have been flagged for moderation. This is the main endpoint moderators 
   use to see which reviews need their attention. The list includes the flag reason so moderators know 
   why each review was flagged.

**Access Control:** Moderator or Admin role required

**Response:** 200 OK with list of flagged reviews

DELETE /reviews/{review_id}
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autofunction:: reviews_service.app.routers.reviews.delete_review

**File:** ``reviews_service/app/routers/reviews.py``

**Description:**
   Permanently deletes a review from the system. Regular users can only delete their own reviews, 
   while admins and moderators can delete any review (useful for removing inappropriate content).

**URL Parameters:**
   - review_id (integer, required): ID of the review to delete

**Access Control:**
   - Regular users: Can only delete own reviews
   - Admin/Moderator: Can delete any review

**Response:** 200 OK with success message

