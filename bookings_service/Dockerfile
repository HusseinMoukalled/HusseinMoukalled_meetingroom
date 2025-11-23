FROM python:3.11-slim

WORKDIR /app

# Copy shared directory
COPY shared/ /app/shared/
# Copy bookings service
COPY bookings_service/ /app/bookings_service/
# Copy users service (needed for authentication)
COPY users_service/ /app/users_service/
# Copy rooms service model
COPY rooms_service/app/models.py /app/rooms_service/app/models.py

# Install dependencies with increased timeout
RUN pip install --no-cache-dir --default-timeout=100 -r bookings_service/requirements.txt

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Expose port
EXPOSE 8003

# Run the application
CMD ["uvicorn", "bookings_service.app.main:app", "--host", "0.0.0.0", "--port", "8003"]

