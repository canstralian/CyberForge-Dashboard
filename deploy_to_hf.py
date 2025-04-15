"""
Test script to deploy from Replit to Hugging Face Spaces.
This script simulates the GitHub Actions workflow but runs directly from Replit.
"""
import os
import subprocess
import shutil
import tempfile

def run_command(command):
    """Run a shell command and print output."""
    print(f"Running: {command}")
    process = subprocess.run(command, shell=True, capture_output=True, text=True)
    if process.returncode != 0:
        print("Error:", process.stderr)
        return False
    print("Output:", process.stdout)
    return True

def main():
    # Configuration
    hf_username = "S-Dreamer"
    hf_space_name = "CyberForge"
    
    # Check if HF_TOKEN is available
    hf_token = os.environ.get("HF_TOKEN")
    if not hf_token:
        print("Error: HF_TOKEN environment variable is not set.")
        print("Please set it in Replit Secrets.")
        return
    
    print(f"Deploying to Hugging Face Space: {hf_username}/{hf_space_name}")
    
    # Create a temporary directory for the HF repo
    with tempfile.TemporaryDirectory() as temp_dir:
        # Clone the HF space repository
        clone_cmd = f"git clone https://{hf_username}:{hf_token}@huggingface.co/spaces/{hf_username}/{hf_space_name} {temp_dir}"
        if not run_command(clone_cmd):
            print("Failed to clone repository. Check your token and space name.")
            return
        
        # Create directory structure
        os.makedirs(f"{temp_dir}/assets", exist_ok=True)
        os.makedirs(f"{temp_dir}/components", exist_ok=True)
        os.makedirs(f"{temp_dir}/src", exist_ok=True)
        
        # Copy main files
        shutil.copy("hf_app.py", f"{temp_dir}/")
        shutil.copy("hf_database.py", f"{temp_dir}/")
        shutil.copy("huggingface-space.yml", f"{temp_dir}/")
        shutil.copy("requirements_hf.txt", f"{temp_dir}/requirements.txt")
        
        # Copy assets
        if os.path.exists("assets"):
            for item in os.listdir("assets"):
                s = os.path.join("assets", item)
                d = os.path.join(f"{temp_dir}/assets", item)
                if os.path.isdir(s):
                    shutil.copytree(s, d, dirs_exist_ok=True)
                else:
                    shutil.copy2(s, d)
        
        # Copy components
        if os.path.exists("components"):
            for item in os.listdir("components"):
                s = os.path.join("components", item)
                d = os.path.join(f"{temp_dir}/components", item)
                if os.path.isdir(s):
                    shutil.copytree(s, d, dirs_exist_ok=True)
                else:
                    shutil.copy2(s, d)
        
        # Copy src files needed for HF mode
        if os.path.exists("src/models"):
            shutil.copytree("src/models", f"{temp_dir}/src/models", dirs_exist_ok=True)
        
        for file in ["database_init.py", "streamlit_database.py", "streamlit_subscription_services.py"]:
            if os.path.exists(f"src/{file}"):
                shutil.copy(f"src/{file}", f"{temp_dir}/src/")
        
        # Configure git and commit changes
        os.chdir(temp_dir)
        run_command("git config --global user.email 'replit@example.com'")
        run_command("git config --global user.name 'Replit Deployment'")
        run_command("git add -A")
        run_command("git commit -m 'Deployment from Replit'")
        
        # Push to Hugging Face
        if run_command("git push"):
            print("\n✅ Successfully deployed to Hugging Face Spaces!")
            print(f"View your space at: https://huggingface.co/spaces/{hf_username}/{hf_space_name}")
        else:
            print("\n❌ Failed to push to Hugging Face Spaces.")

if __name__ == "__main__":
    main()