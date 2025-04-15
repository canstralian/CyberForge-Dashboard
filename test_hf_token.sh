#!/bin/bash
# Simple script to test if your Hugging Face token has correct permissions

# Check if token is set
if [ -z "$HF_TOKEN" ]; then
  echo "Error: HF_TOKEN environment variable is not set."
  echo "Please set it in Replit Secrets."
  exit 1
fi

echo "Testing your Hugging Face token..."

# Check token format (only showing first few characters for security)
TOKEN_LENGTH=${#HF_TOKEN}
echo "Token length: $TOKEN_LENGTH characters"
echo "Token starts with: ${HF_TOKEN:0:4}..."

# Test if we can authenticate with verbose output
echo "Sending authentication request to Hugging Face API..."
AUTH_RESPONSE=$(curl -v -s -H "Authorization: Bearer $HF_TOKEN" https://huggingface.co/api/whoami 2>&1)
if echo "$AUTH_RESPONSE" | grep -q "user"; then
  echo "✅ Authentication successful!"
  USERNAME=$(echo "$AUTH_RESPONSE" | grep -o '"name":"[^"]*' | cut -d'"' -f4)
  echo "Logged in as: $USERNAME"
else
  echo "❌ Authentication failed. Please check your HF_TOKEN."
  echo "Response from Hugging Face API:"
  echo "$AUTH_RESPONSE"
  exit 1
fi

# Check if we have write access to the space
HF_USERNAME="S-Dreamer"
HF_SPACE_NAME="CyberForge"
SPACE_URL="https://huggingface.co/api/spaces/$HF_USERNAME/$HF_SPACE_NAME"

echo "Checking permissions for Space: $HF_USERNAME/$HF_SPACE_NAME..."

SPACE_RESPONSE=$(curl -s -H "Authorization: Bearer $HF_TOKEN" "$SPACE_URL")
if echo "$SPACE_RESPONSE" | grep -q "$HF_SPACE_NAME"; then
  echo "✅ Space exists!"
  
  if echo "$SPACE_RESPONSE" | grep -q '"canWrite":true'; then
    echo "✅ You have write access to this Space!"
  else
    echo "❌ You don't have write access to this Space."
    echo "Please make sure your token has write permissions or you are the owner of the space."
  fi
else
  echo "❌ Space not found or you don't have access to it."
  echo "Response from Hugging Face API:"
  echo "$SPACE_RESPONSE"
fi