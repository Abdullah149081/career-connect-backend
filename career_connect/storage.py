"""
Custom storage backends for CareerConnect.
This ensures proper file handling in serverless environments like Vercel.
"""

from django.conf import settings
from cloudinary_storage.storage import MediaCloudinaryStorage


class CloudinaryMediaStorage(MediaCloudinaryStorage):
    """
    Custom Cloudinary storage that ensures files are uploaded directly to Cloudinary
    without attempting to write to the local filesystem first.
    This is critical for serverless deployments (Vercel, AWS Lambda, etc.)
    where the filesystem is read-only.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ensure we're using Cloudinary configuration
        if hasattr(settings, 'CLOUDINARY_STORAGE'):
            for key, value in settings.CLOUDINARY_STORAGE.items():
                setattr(self, key.lower(), value)
