FROM python:3.11-slim
USER root

# Set the working directory environment variable
ENV WORK_DIR=/app
ENV BACKEND_HOST=0.0.0.0
ENV BACKEND_PORT=8000
ENV DEPLOYMENT=prod

SHELL ["/bin/bash", "-c"]

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install system dependencies
RUN echo "deb http://deb.debian.org/debian bullseye main" >> /etc/apt/sources.list && \
    apt-get update && \
    apt-get install -y netcat --no-install-recommends && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set up working directory
RUN mkdir -p /app
WORKDIR /app

# Install dependencies
COPY requirements.txt ./
RUN pip install -r requirements.txt --no-cache-dir

# Copy the project files to the working directory
COPY . .

# Copy the entrypoint script
RUN sed -i 's/\r$//g' ./entrypoint.sh
RUN chmod +x ./entrypoint.sh

# Expose the port the app runs on
EXPOSE 8000

# Run the app entrypoint
ENTRYPOINT ["./entrypoint.sh"]