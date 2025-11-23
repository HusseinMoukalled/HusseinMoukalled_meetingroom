FROM python:3.11-slim

WORKDIR /app

# Copy shared directory
COPY shared/ /app/shared/
# Copy rooms service
COPY rooms_service/ /app/rooms_service/
# Copy users service (needed for authentication)
COPY users_service/ /app/users_service/

# Install dependencies with increased timeout
RUN pip install --no-cache-dir --default-timeout=100 -r rooms_service/requirements.txt

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Expose port
EXPOSE 8002

# Run the application
CMD ["uvicorn", "rooms_service.app.main:app", "--host", "0.0.0.0", "--port", "8002"]

