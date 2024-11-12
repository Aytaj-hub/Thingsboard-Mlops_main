# Use an official Python runtime as a base image
FROM python:3.12-slim

# Set the working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Install MLflow and mysqlclient
RUN pip install mlflow mysqlclient

# Expose port 5000 for MLflow
EXPOSE 5000

# Start the MLflow server
CMD ["mlflow", "server"]
