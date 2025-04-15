# Deployment Guide: Replit to GitHub to Hugging Face

This guide provides step-by-step instructions for deploying your CyberForge OSINT Platform from Replit to GitHub, which then automatically deploys to Hugging Face Spaces.

## 1. Setup GitHub Repository

1. Create a new GitHub repository:
   - Go to [GitHub](https://github.com) and sign in
   - Click "New repository"
   - Name it (e.g., "cyberforge-dashboard")
   - Choose visibility (public or private)
   - Do NOT initialize with README, .gitignore, or license
   - Click "Create repository"

## 2. Push from Replit to GitHub

1. Initialize Git in your Replit project (if not already done):
   ```bash
   git init
   ```

2. Add your GitHub repository as a remote:
   ```bash
   git remote add origin https://github.com/YOUR_USERNAME/cyberforge-dashboard.git
   ```

3. Add all files to Git:
   ```bash
   git add .
   ```

4. Commit the changes:
   ```bash
   git commit -m "Initial commit"
   ```

5. Push to GitHub:
   ```bash
   git push -u origin main
   ```
   
   If your default branch is "master" instead of "main", use:
   ```bash
   git push -u origin master
   ```

## 3. Setup Hugging Face Space

1. Go to [Hugging Face Spaces](https://huggingface.co/spaces)
2. Click "Create Space"
3. Fill in the details:
   - Owner: "S-Dreamer"
   - Name: "CyberForge"
   - SDK: Select "Streamlit"
   - License: Choose "MIT" or another license
   - Visibility: Public or private
4. Click "Create Space"

## 4. Configure GitHub Repository Secrets

1. Go to your GitHub repository
2. Click on "Settings" > "Secrets and variables" > "Actions"
3. Click "New repository secret"
4. Add the following secrets:
   - Name: `HF_TOKEN`
     Value: Your Hugging Face API token (from [Hugging Face settings](https://huggingface.co/settings/tokens))
   - Name: `HF_USERNAME`
     Value: `S-Dreamer` (your Hugging Face username)
   - Name: `HF_SPACE_NAME`
     Value: `CyberForge` (your Hugging Face Space name)

## 5. Trigger GitHub Actions Workflow

The workflow will automatically run when you push to your main branch. 

To manually trigger it:
1. Go to your GitHub repository
2. Click on "Actions"
3. Select "Deploy to Hugging Face Spaces" workflow
4. Click "Run workflow"
5. Select the branch and click "Run workflow"

## 6. Verify Deployment

1. Go to your Hugging Face Space at `https://huggingface.co/spaces/S-Dreamer/CyberForge`
2. The deployment might take a few minutes to complete
3. Once completed, you should see the CyberForge OSINT Platform running in demo mode

## Troubleshooting

If you encounter issues:

1. Check GitHub Actions logs for error messages
2. Verify your Hugging Face token has proper permissions
3. Make sure the repository secrets are correctly set
4. Check that the `.github/workflows/deploy-to-huggingface.yml` file exists in your repository

## Updating the Deployment

Any future pushes to your main branch will automatically trigger a new deployment. Simply make your changes in Replit, commit, and push to GitHub.