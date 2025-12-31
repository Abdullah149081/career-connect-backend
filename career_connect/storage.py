"""
Custom storage backends for CareerConnect.
This ensures proper file handling in serverless environments like Vercel.
"""

import os
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
        # Initialize parent class which handles Cloudinary configuration
        super().__init__(*args, **kwargs)
    
    def path(self, name):
        """
        Override to prevent any filesystem path operations.
        In serverless environments, we should never access local paths.
        """
        raise NotImplementedError("This backend doesn't support absolute paths.")
    
    def get_available_name(self, name, max_length=None):
        """
        Override to prevent filesystem checks for existing files.
        Let Cloudinary handle filename conflicts.
        """
        # Return the name as-is, Cloudinary will handle duplicates
        return name
    
    def exists(self, name):
        """
        Override to prevent filesystem checks.
        Always return False to force upload to Cloudinary.
        """
        return False
    
    def listdir(self, path):
        """
        Override to prevent directory listing operations on filesystem.
        """
        raise NotImplementedError("This backend doesn't support directory listing.")
    
    def size(self, name):
        """
        Override to get file size from Cloudinary instead of filesystem.
        """
        try:
            return super().size(name)
        except:
            return 0
    
    def url(self, name):
        """
        Return the Cloudinary URL for the file.
        """
        try:
            return super().url(name)
        except:
            # Fallback to a basic Cloudinary URL
            return f"https://res.cloudinary.com/{settings.CLOUDINARY_STORAGE['CLOUD_NAME']}/raw/upload/{name}"
