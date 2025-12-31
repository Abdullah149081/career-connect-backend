from django.shortcuts import redirect
from django.http import JsonResponse
from django.conf import settings


def api_root_view(request):
    """Redirect to the API root endpoint."""
    return redirect("api-root")


def debug_config(request):
    """Debug endpoint to check configuration."""
    cloudinary_status = {
        "cloudinary_configured": bool(settings.CLOUDINARY_CLOUD_NAME),
        "cloud_name": settings.CLOUDINARY_CLOUD_NAME[:5] + "***" if settings.CLOUDINARY_CLOUD_NAME else "NOT SET",
        "api_key_set": bool(settings.CLOUDINARY_API_KEY),
        "api_secret_set": bool(settings.CLOUDINARY_API_SECRET),
        "default_file_storage": settings.DEFAULT_FILE_STORAGE,
        "media_url": settings.MEDIA_URL,
        "media_root": str(settings.MEDIA_ROOT) if settings.MEDIA_ROOT else "None",
        "debug": settings.DEBUG,
    }
    return JsonResponse(cloudinary_status)
