import sys
import os

# Ensure the project root is in the python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from backend.config import settings
from backend.utils.cloudinary_service import configure_cloudinary

def test_cloudinary_config():
    print("Testing Cloudinary configuration...")
    try:
        configure_cloudinary()
        print(f"Cloud Name: {settings.cloudinary_cloud_name}")
        print("Configuration loaded successfully.")
        return True
    except Exception as e:
        print(f"Configuration failed: {e}")
        return False

if __name__ == "__main__":
    if test_cloudinary_config():
        sys.exit(0)
    else:
        sys.exit(1)
