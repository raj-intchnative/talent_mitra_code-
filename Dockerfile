# Use official Python image
FROM python:3.11

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV GOOGLE_APPLICATION_CREDENTIALS="/app/credentials.json"

# Set working directory
WORKDIR /app

# Copy and install dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . /app/

# Copy credentials securely
COPY credentials.json /app/credentials.json

# Expose the port for Cloud Run
EXPOSE 8080

# Start the application
CMD ["gunicorn", "-b", "0.0.0.0:8080", "TalentMitra.wsgi"]
