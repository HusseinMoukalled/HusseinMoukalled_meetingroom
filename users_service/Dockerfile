FROM python:3.11-slim

WORKDIR /app

# Copy shared directory
COPY shared/ /app/shared/
COPY users_service/ /app/users_service/

# Install dependencies with increased timeout
RUN pip install --no-cache-dir --default-timeout=100 -r users_service/requirements.txt

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Expose port
EXPOSE 8001

# Run the application
CMD ["uvicorn", "users_service.app.main:app", "--host", "0.0.0.0", "--port", "8001"]

