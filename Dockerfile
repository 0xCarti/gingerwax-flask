# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set environment variables for production
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_ENV=production \
    FLASK_DEBUG=0

# Set the working directory in the container
WORKDIR /app

# Copy only the requirements.txt to the working directory
COPY requirements.txt /app/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir gunicorn

# Copy the rest of the application code
COPY . /app

# Expose the port your Flask/Gunicorn app will run on
EXPOSE 5000

# Use Gunicorn for a production server
#  -b 0.0.0.0:5000 binds to all interfaces on port 5000
#  -w 4 (for example) uses 4 worker processes
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
