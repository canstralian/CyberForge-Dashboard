#!/bin/bash
# Deploy to Hugging Face Spaces directly from Replit
# This script simulates the GitHub Actions workflow

# Configuration
HF_USERNAME="S-Dreamer"
HF_SPACE_NAME="CyberForge"

# Check if token is set
if [ -z "$HF_TOKEN" ]; then
  echo "Error: HF_TOKEN environment variable is not set."
  echo "Please set it in Replit Secrets."
  exit 1
fi

echo "Deploying to Hugging Face Space: $HF_USERNAME/$HF_SPACE_NAME"

# Create a temporary directory
TEMP_DIR=$(mktemp -d)
echo "Using temporary directory: $TEMP_DIR"

# Set up Git credentials helper to use the token
git config --global credential.helper store
echo "https://$HF_USERNAME:$HF_TOKEN@huggingface.co" > ~/.git-credentials
chmod 600 ~/.git-credentials

# Skip initial authentication test and proceed directly to git operations
echo "Skipping initial authentication test and proceeding with git operations..."
echo "This will use your token directly with git commands."

# Clone the Hugging Face space repository
echo "Cloning Hugging Face Space repository..."
git clone https://$HF_USERNAME:$HF_TOKEN@huggingface.co/spaces/$HF_USERNAME/$HF_SPACE_NAME $TEMP_DIR
if [ $? -ne 0 ]; then
  echo "Failed to clone repository. Check your space name and permissions."
  echo "Trying alternative clone method..."
  # Try using https URL with token in credentials
  git clone "https://api-token:$HF_TOKEN@huggingface.co/spaces/$HF_USERNAME/$HF_SPACE_NAME" $TEMP_DIR
  if [ $? -ne 0 ]; then
    echo "All clone attempts failed. Please verify your token has appropriate permissions."
    exit 1
  fi
fi

# Create directory structure
mkdir -p $TEMP_DIR/assets
mkdir -p $TEMP_DIR/components
mkdir -p $TEMP_DIR/src

# Copy main files
cp hf_app.py $TEMP_DIR/app.py  # Copy hf_app.py as app.py for Hugging Face
cp hf_database.py $TEMP_DIR/
cp huggingface-space.yml $TEMP_DIR/
cp requirements_hf.txt $TEMP_DIR/requirements.txt
cp security_hf.py $TEMP_DIR/  # Copy simplified security module

# Copy assets
if [ -d "assets" ]; then
  cp -r assets/* $TEMP_DIR/assets/ 2>/dev/null || :
fi

# Copy components
if [ -d "components" ]; then
  cp -r components/* $TEMP_DIR/components/ 2>/dev/null || :
fi

# Copy src files needed for HF mode
# Create necessary directories
mkdir -p $TEMP_DIR/src/models
mkdir -p $TEMP_DIR/src/api
mkdir -p $TEMP_DIR/src/api/services

# Copy model files
if [ -d "src/models" ]; then
  cp -r src/models/* $TEMP_DIR/src/models/ 2>/dev/null || :
fi

# Copy API files
if [ -d "src/api" ]; then
  # Copy security.py and other essential API files
  for file in $(find src/api -name "*.py" | grep -v "__pycache__"); do
    # Create target directory
    target_dir=$(dirname "${file}" | sed "s|^src|$TEMP_DIR/src|")
    mkdir -p "$target_dir"
    # Copy file
    cp "$file" "$target_dir/" 2>/dev/null || :
  done
fi

# Copy specific src files
for file in "database_init.py" "streamlit_database.py" "streamlit_subscription_services.py" "__init__.py"; do
  if [ -f "src/$file" ]; then
    cp "src/$file" "$TEMP_DIR/src/"
  fi
done

# Ensure __init__.py files exist in all directories for proper imports
touch "$TEMP_DIR/src/__init__.py"
touch "$TEMP_DIR/src/api/__init__.py"
touch "$TEMP_DIR/src/api/services/__init__.py"
touch "$TEMP_DIR/src/models/__init__.py"

# Configure git and commit changes
cd $TEMP_DIR
git config --global user.email "replit@example.com"
git config --global user.name "Replit Deployment"
git add -A
git commit -m "Deployment from Replit"

# Push to Hugging Face with credentials in URL
if git push https://$HF_USERNAME:$HF_TOKEN@huggingface.co/spaces/$HF_USERNAME/$HF_SPACE_NAME; then
  echo -e "\n✅ Successfully deployed to Hugging Face Spaces!"
  echo "View your space at: https://huggingface.co/spaces/$HF_USERNAME/$HF_SPACE_NAME"
else
  echo "Trying alternative push method..."
  if git push https://api-token:$HF_TOKEN@huggingface.co/spaces/$HF_USERNAME/$HF_SPACE_NAME; then
    echo -e "\n✅ Successfully deployed to Hugging Face Spaces!"
    echo "View your space at: https://huggingface.co/spaces/$HF_USERNAME/$HF_SPACE_NAME"
  else
    echo -e "\n❌ Failed to push to Hugging Face Spaces."
    echo "Please check your token permissions and make sure you have write access to the space."
  fi
fi

# Cleanup
cd - > /dev/null
echo "Cleaning up temporary files..."
rm -rf $TEMP_DIR

# Remove credentials
if [ -f ~/.git-credentials ]; then
  rm ~/.git-credentials
fi
git config --global --unset credential.helper