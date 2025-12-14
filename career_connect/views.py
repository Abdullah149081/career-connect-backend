from django.shortcuts import redirect


def api_root_view(request):
    """Redirect to the API root endpoint."""
    return redirect("api-root")
