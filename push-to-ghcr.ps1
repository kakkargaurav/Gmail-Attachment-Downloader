# PowerShell script to manually push Docker image to GitHub Container Registry
# Usage: ./push-to-ghcr.ps1 [username] [version]

param(
    [Parameter(Mandatory=$true)]
    [string]$Username,
    [string]$Version = "latest"
)

$IMAGE_NAME = "gmail-downloader"
$REGISTRY = "ghcr.io"
$FULL_IMAGE_NAME = "$REGISTRY/$Username/$IMAGE_NAME"

Write-Host "Building and pushing Docker image to GitHub Container Registry..." -ForegroundColor Green
Write-Host "Registry: $REGISTRY" -ForegroundColor Yellow
Write-Host "Image: $FULL_IMAGE_NAME:$Version" -ForegroundColor Yellow

# Build the image with the correct tag
Write-Host "`nStep 1: Building Docker image..." -ForegroundColor Cyan
docker build -t "$FULL_IMAGE_NAME:$Version" .

if ($LASTEXITCODE -ne 0) {
    Write-Host "Docker build failed!" -ForegroundColor Red
    exit 1
}

# Tag as latest if version is not latest
if ($Version -ne "latest") {
    Write-Host "`nStep 2: Tagging as latest..." -ForegroundColor Cyan
    docker tag "$FULL_IMAGE_NAME:$Version" "$FULL_IMAGE_NAME:latest"
}

# Login to GitHub Container Registry
Write-Host "`nStep 3: Logging in to GitHub Container Registry..." -ForegroundColor Cyan
Write-Host "Please enter your GitHub Personal Access Token with package:write permissions:"
docker login $REGISTRY -u $Username

if ($LASTEXITCODE -ne 0) {
    Write-Host "Login failed!" -ForegroundColor Red
    exit 1
}

# Push the image
Write-Host "`nStep 4: Pushing image to registry..." -ForegroundColor Cyan
docker push "$FULL_IMAGE_NAME:$Version"

if ($Version -ne "latest") {
    docker push "$FULL_IMAGE_NAME:latest"
}

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n✅ Successfully pushed to GitHub Container Registry!" -ForegroundColor Green
    Write-Host "Image is available at: $FULL_IMAGE_NAME:$Version" -ForegroundColor Yellow
    Write-Host "`nTo pull the image:" -ForegroundColor Cyan
    Write-Host "docker pull $FULL_IMAGE_NAME:$Version" -ForegroundColor White
} else {
    Write-Host "❌ Push failed!" -ForegroundColor Red
    exit 1
}