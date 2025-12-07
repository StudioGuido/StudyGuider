
# FROM nvidia/cuda:11.8.0-runtime-ubuntu22.04

# # Install Python & system deps
# RUN apt-get update && apt-get install -y \
#     python3 python3-pip libpq-dev gcc \
#   && rm -rf /var/lib/apt/lists/*

# WORKDIR /app
#------------------
# Base image with Ubuntu + Python
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies (including PostgreSQL client)
RUN apt-get update && apt-get install -y \
    libpq-dev gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the app
COPY backend/ .

# Expose FastAPI default port
EXPOSE 8000

# Make the entrypoint script executable
# FROM nvidia/cuda:11.8.0-runtime-ubuntu22.04

# # Install Python & system deps
# RUN apt-get update && apt-get install -y \
#     python3 python3-pip libpq-dev gcc \
#   && rm -rf /var/lib/apt/lists/*

# WORKDIR /app
#------------------
# Base image with Ubuntu + Python
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies (including PostgreSQL client)
RUN apt-get update && apt-get install -y \
    libpq-dev gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the app
COPY backend/ .

# Expose FastAPI default port
EXPOSE 8000

# Make the entrypoint script executable
RUN chmod +x entrypoint.sh

# Use entrypoint.sh as the container startup command
ENTRYPOINT ["/app/entrypoint.sh"]

# # Run the FastAPI app with uvicorn
# CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

RUN chmod +x entrypoint.sh

# Use entrypoint.sh as the container startup command
ENTRYPOINT ["/app/entrypoint.sh"]

# # Run the FastAPI app with uvicorn
# CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
