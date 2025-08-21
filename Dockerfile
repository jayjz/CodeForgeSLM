# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies required for Git and building some Python packages
RUN apt-get update && apt-get install -y \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the container
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project into the container
COPY . .

# Create directories for temporary repositories and logs
RUN mkdir -p temp_repos logs

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application using Uvicorn
# This will start the FastAPI server defined in api/main.py
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]