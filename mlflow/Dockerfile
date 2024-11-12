# mlflow/Dockerfile

# Use an official Python runtime as a base image
FROM python:3.8-slim

# Set the working directory
WORKDIR /app

# Install MLflow
RUN pip install mlflow

# Expose port 5000 for MLflow
EXPOSE 5000

# Start the MLflow server
CMD ["mlflow", "server"]