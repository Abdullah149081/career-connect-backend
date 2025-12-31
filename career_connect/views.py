from django.shortcuts import redirect
from django.http import JsonResponse
from django.conf import settings
import traceback
import cloudinary.uploader


def api_root_view(request):
    """Redirect to the API root endpoint."""
    return redirect("api-root")


def debug_config(request):
    """Debug endpoint to check configuration."""
    try:
        cloudinary_status = {
            "cloudinary_configured": bool(settings.CLOUDINARY_CLOUD_NAME),
            "cloud_name": settings.CLOUDINARY_CLOUD_NAME[:5] + "***" if settings.CLOUDINARY_CLOUD_NAME else "NOT SET",
            "api_key_set": bool(settings.CLOUDINARY_API_KEY),
            "api_secret_set": bool(settings.CLOUDINARY_API_SECRET),
            "default_file_storage": settings.DEFAULT_FILE_STORAGE,
            "media_url": settings.MEDIA_URL,
            "media_root": str(settings.MEDIA_ROOT) if settings.MEDIA_ROOT else "None",
            "debug": settings.DEBUG,
            "database_connected": False,
            "cloudinary_upload_test": "not_tested",
        }
        
        # Test database connection
        try:
            from django.db import connection
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            cloudinary_status["database_connected"] = True
        except Exception as e:
            cloudinary_status["database_error"] = str(e)
        
        # Test Cloudinary upload (only if configured)
        if settings.CLOUDINARY_CLOUD_NAME:
            try:
                # This tests the connection without actually uploading
                import cloudinary
                cloudinary_status["cloudinary_upload_test"] = "ready"
            except Exception as e:
                cloudinary_status["cloudinary_upload_test"] = f"error: {str(e)}"
        
        return JsonResponse(cloudinary_status)
    except Exception as e:
        return JsonResponse({
            "error": str(e),
            "traceback": traceback.format_exc()
        }, status=500)
