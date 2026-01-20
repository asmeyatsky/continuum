#!/bin/bash

# Deployment script for Continuum on VM

echo "🚀 Starting deployment..."

# 1. Pull latest code
echo "📥 Pulling latest code..."
git pull

# 2. Build and start containers
echo "🐳 Building and starting containers..."
# Use the production compose file
docker-compose -f docker-compose.prod.yml up -d --build

# 3. Prune unused images to save space
echo "🧹 Cleaning up..."
docker image prune -f

echo "✅ Deployment complete! System is running."
echo "   API: http://localhost:8000"
echo "   DB:  localhost:5432"
