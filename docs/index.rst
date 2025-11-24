Hussein's Meeting Room Management System Documentation
====================================================

Welcome to the comprehensive documentation for Hussein's Meeting Room & Management System Backend.

This system consists of four microservices that work together to provide a complete meeting room management solution. Each service is documented in detail below with all functions, endpoints, and their implementations.

**Project:** Hussein's Meeting Room Management System  
**Author:** Hussein Moukalled  
**Date:** Fall 2025-2026

Overview
--------

Hussein's Meeting Room Management System is a backend application built with FastAPI that provides:

* **User Management:** Registration, authentication, profile management, and role-based access control
* **Room Management:** Add, update, delete rooms, check availability, and filter by capacity/location/equipment
* **Booking Management:** Create, update, cancel bookings with conflict prevention and availability checking
* **Review System:** Submit reviews, ratings, and moderation features for inappropriate content

All services are containerized using Docker and communicate through well-defined REST APIs.

Services Documentation
----------------------

Detailed documentation for each service:

.. toctree::
   :maxdepth: 2

   services
   users_service
   rooms_service
   bookings_service
   reviews_service

API Reference
--------------

Complete API documentation organized by service:

.. toctree::
   :maxdepth: 2

   api
   users_service
   rooms_service
   bookings_service
   reviews_service

Authentication & Security
--------------------------

.. toctree::
   :maxdepth: 2

   authentication

Database Schema
---------------

.. toctree::
   :maxdepth: 2

   database

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

