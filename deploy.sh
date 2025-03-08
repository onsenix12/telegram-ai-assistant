#!/bin/bash

# Script to deploy the Telegram AI Assistant

set -e  # Exit immediately if a command exits with a non-zero status

# Display current directory
echo "Current directory: $(pwd)"

# Pull the latest code (if deployed with git)
if [ -d ".git" ]; then
  echo "Pulling latest changes..."
  git pull
fi

# Set environment variables from .env file
if [ -f ".env" ]; then
  echo "Loading environment variables..."
  export $(grep -v '^#' .env | xargs)
fi

# Set the Docker image name
export DOCKER_IMAGE=${DOCKER_IMAGE:-$DOCKERHUB_USERNAME/telegram-ai-assistant:latest}
echo "Using Docker image: $DOCKER_IMAGE"

# Stop and remove existing containers
echo "Stopping existing containers..."
docker-compose -f docker-compose.prod.yml down || true

# Pull the latest images
echo "Pulling latest images..."
docker-compose -f docker-compose.prod.yml pull

# Start the containers
echo "Starting containers..."
docker-compose -f docker-compose.prod.yml up -d

# Display running containers
echo "Running containers:"
docker-compose -f docker-compose.prod.yml ps

echo "Deployment completed successfully!"