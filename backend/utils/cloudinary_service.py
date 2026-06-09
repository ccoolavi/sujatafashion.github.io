import cloudinary
import cloudinary.uploader
from backend.config import settings

def configure_cloudinary():
    """Configures the Cloudinary SDK with settings from the application config."""
    cloudinary.config(
        cloud_name=settings.cloudinary_cloud_name,
        api_key=settings.cloudinary_api_key,
        api_secret=settings.cloudinary_api_secret,
        secure=True
    )

def upload_image(file_path: str, folder: str = "sfa_assets") -> dict:
    """
    Uploads an image to Cloudinary.
    
    Args:
        file_path: Path to the file to upload.
        folder: Cloudinary folder to upload to.
        
    Returns:
        A dictionary containing the Cloudinary upload response.
    """
    try:
        result = cloudinary.uploader.upload(
            file_path,
            folder=folder
        )
        return {"success": True, "data": result}
    except Exception as e:
        return {"success": False, "error": str(e)}

def delete_image(public_id: str) -> dict:
    """
    Deletes an image from Cloudinary.
    
    Args:
        public_id: The public ID of the image to delete.
        
    Returns:
        A dictionary containing the Cloudinary deletion response.
    """
    try:
        result = cloudinary.uploader.destroy(public_id)
        return {"success": True, "data": result}
    except Exception as e:
        return {"success": False, "error": str(e)}
