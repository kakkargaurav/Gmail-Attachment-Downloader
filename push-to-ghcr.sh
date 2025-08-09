#!/bin/bash

# Bash script to manually push Docker image to GitHub Container Registry
# Usage: ./push-to-ghcr.sh [username] [version]

set -e

# Check if username is provided
if [ -z "$1" ]; then
    echo "❌ Error: Username is required"
    echo "Usage: $0 <github-username> [version]"
    echo "Example: $0 myusername v1.0.0"
    exit 1
fi

USERNAME="$1"
VERSION="${2:-latest}"
IMAGE_NAME="gmail-downloader"
REGISTRY="ghcr.io"
FULL_IMAGE_NAME="$REGISTRY/$USERNAME/$IMAGE_NAME"

echo "🚀 Building and pushing Docker image to GitHub Container Registry..."
echo "📦 Registry: $REGISTRY"
echo "🏷️  Image: $FULL_IMAGE_NAME:$VERSION"

# Build the image with the correct tag
echo ""
echo "📋 Step 1: Building Docker image..."
docker build -t "$FULL_IMAGE_NAME:$VERSION" .

# Tag as latest if version is not latest
if [ "$VERSION" != "latest" ]; then
    echo ""
    echo "🏷️  Step 2: Tagging as latest..."
    docker tag "$FULL_IMAGE_NAME:$VERSION" "$FULL_IMAGE_NAME:latest"
fi

# Login to GitHub Container Registry
echo ""
echo "🔐 Step 3: Logging in to GitHub Container Registry..."
echo "Please enter your GitHub Personal Access Token with package:write permissions:"
echo "$REGISTRY" | docker login --username "$USERNAME" --password-stdin "$REGISTRY"

# Push the image
echo ""
echo "📤 Step 4: Pushing image to registry..."
docker push "$FULL_IMAGE_NAME:$VERSION"

if [ "$VERSION" != "latest" ]; then
    docker push "$FULL_IMAGE_NAME:latest"
fi

echo ""
echo "✅ Successfully pushed to GitHub Container Registry!"
echo "🎯 Image is available at: $FULL_IMAGE_NAME:$VERSION"
echo ""
echo "🐳 To pull the image:"
echo "docker pull $FULL_IMAGE_NAME:$VERSION"
echo ""
echo "🔧 To run the container:"
echo "docker run -v \$(pwd)/downloads:/app/downloads \\"
echo "           -v \$(pwd)/credentials:/app/credentials \\"
echo "           -e SEARCH_QUERY=\"has:attachment\" \\"
echo "           $FULL_IMAGE_NAME:$VERSION"