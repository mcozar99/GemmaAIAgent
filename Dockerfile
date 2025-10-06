# Use official Python image
FROM python:3.11-slim

# Set work directory
WORKDIR /app

# Copy requirements and install dependencies
COPY src/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy app source code
COPY src/ ./

# Expose port (Fly.io default is 8080)
EXPOSE 8080

# Set environment variables (optional)
ENV PYTHONUNBUFFERED=1

# Command to run the app (adjust if you use gunicorn/uvicorn)
CMD ["python", "app.py"]
