FROM python:3.11-slim

WORKDIR /app

# Copy shared directory
COPY shared/ /app/shared/
# Copy reviews service
COPY reviews_service/ /app/reviews_service/
# Copy users service (needed for authentication)
COPY users_service/ /app/users_service/
# Copy rooms service model
COPY rooms_service/app/models.py /app/rooms_service/app/models.py

# Install dependencies with increased timeout
RUN pip install --no-cache-dir --default-timeout=100 -r reviews_service/requirements.txt

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
    
# Expose port
EXPOSE 8004

# Run the application
CMD ["uvicorn", "reviews_service.app.main:app", "--host", "0.0.0.0", "--port", "8004"]

