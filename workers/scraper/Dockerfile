FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Run the Celery worker
CMD ["celery", "-A", "shared.celery_app", "worker", "-Q", "scraper", "--loglevel=info", "-n", "scraper_worker@%h"]