#!/bin/bash

# Script to deploy the application to Hugging Face Spaces

# Check if required environment variables are set
if [ -z "$HF_TOKEN" ]; then
    echo "Error: HF_TOKEN environment variable not set"
    exit 1
fi

if [ -z "$HF_USERNAME" ]; then
    echo "Error: HF_USERNAME environment variable not set"
    exit 1
fi

# Default space name if not provided
SPACE_NAME=${HF_SPACE_NAME:-cyberforge-dashboard}

echo "Deploying to Hugging Face Space: $HF_USERNAME/$SPACE_NAME"

# Create the space if it doesn't exist
echo "Creating/updating space configuration..."
curl -X POST \
    -H "Authorization: Bearer $HF_TOKEN" \
    -H "Content-Type: application/json" \
    -d "{\"private\": false, \"sdk\": \"streamlit\"}" \
    https://huggingface.co/api/spaces/$HF_USERNAME/$SPACE_NAME

# Clone the space repository
echo "Cloning space repository..."
git clone https://huggingface.co/spaces/$HF_USERNAME/$SPACE_NAME hf_space
cd hf_space

# Copy all files to the cloned repository
echo "Copying application files..."
cp -r ../* .
cp ../huggingface-space.yml ./.huggingface/space.yml
cp ../requirements_hf.txt ./requirements.txt

# Commit and push changes
echo "Committing and pushing changes..."
git add .
git config --global user.email "actions@github.com"
git config --global user.name "GitHub Actions"
git commit -m "Update space from GitHub Actions"
git push https://$HF_USERNAME:$HF_TOKEN@huggingface.co/spaces/$HF_USERNAME/$SPACE_NAME main

echo "Deployment completed!"