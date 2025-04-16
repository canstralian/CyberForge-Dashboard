"""
Run the Alembic migration to create deployment tables.
"""
import os
import subprocess
import sys

def run_alembic_command(command):
    """Run an Alembic command and print the output."""
    print(f"Executing: alembic {command}")
    
    try:
        result = subprocess.run(
            f"alembic {command}",
            shell=True,
            check=True,
            capture_output=True,
            text=True
        )
        print(result.stdout)
        if result.stderr:
            print(f"Stderr: {result.stderr}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Command failed with exit code {e.returncode}")
        print(f"Stdout: {e.stdout}")
        print(f"Stderr: {e.stderr}")
        return False

def main():
    """Run Alembic migration."""
    # Check if the migrations directory exists
    if not os.path.isdir("migrations"):
        print("Error: 'migrations' directory not found")
        sys.exit(1)
    
    # Check if the versions directory exists
    if not os.path.isdir("migrations/versions"):
        print("Error: 'migrations/versions' directory not found")
        sys.exit(1)
    
    # Run the migration
    if not run_alembic_command("upgrade head"):
        print("Migration failed")
        sys.exit(1)
    
    print("Migration completed successfully")

if __name__ == "__main__":
    main()