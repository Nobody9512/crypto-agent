FROM python:3.10-slim

WORKDIR /app

# System dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libc6-dev \
    && rm -rf /var/lib/apt/lists/*

# Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Make sure we have a data directory for the database
RUN mkdir -p /app/data

# Set environment variable for database location
ENV DATABASE_NAME=/app/data/crypto_news.db

# Run the bot
CMD ["python", "main.py"] 