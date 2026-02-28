# Use official Python lightweight image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirement files and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy main application file
COPY main.py .

# Run the FastAPI server on Railway's default port (PORT env variable)
CMD uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}
