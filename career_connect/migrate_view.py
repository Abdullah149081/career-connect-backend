"""
View to run database migrations remotely on Vercel.
Access this endpoint after deployment to run migrations.
"""

from django.http import JsonResponse
from django.core.management import call_command
from django.views.decorators.csrf import csrf_exempt
from decouple import config
import io


@csrf_exempt
def run_migrations(request):
    """
    Run database migrations.
    Requires MIGRATION_SECRET in environment variables for security.

    Usage: GET /run-migrations/?secret=YOUR_MIGRATION_SECRET
    """
    # Security check - require a secret key
    migration_secret = config("MIGRATION_SECRET", default="")
    provided_secret = request.GET.get("secret", "")

    if not migration_secret:
        return JsonResponse(
            {
                "error": "MIGRATION_SECRET not configured",
                "message": "Set MIGRATION_SECRET environment variable",
            },
            status=500,
        )

    if provided_secret != migration_secret:
        return JsonResponse(
            {"error": "Unauthorized", "message": "Invalid or missing secret parameter"},
            status=403,
        )

    try:
        # Capture migration output
        out = io.StringIO()

        # Run migrations
        call_command("migrate", stdout=out, interactive=False)

        output = out.getvalue()

        return JsonResponse(
            {
                "status": "success",
                "message": "Migrations completed successfully",
                "output": output,
            }
        )

    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)
