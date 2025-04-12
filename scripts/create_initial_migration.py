#!/usr/bin/env python
"""Script to create the initial Alembic migration."""
import os
import subprocess
import sys

def main():
    """Create initial Alembic migration."""
    try:
        # Run alembic revision command
        subprocess.run(
            [
                "alembic", 
                "revision", 
                "--autogenerate", 
                "-m", 
                "Create initial tables"
            ],
            check=True
        )
        print("Successfully created initial migration.")
    except subprocess.CalledProcessError as e:
        print(f"Error creating migration: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()