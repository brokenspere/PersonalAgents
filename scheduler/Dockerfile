FROM python:3.11-slim

WORKDIR /app

# Install dependencies first for better layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project (respecting .dockerignore)
COPY . .

# Run the Celery beat scheduler
CMD ["celery", "-A", "shared.celery_app", "beat", "--loglevel=info"]
