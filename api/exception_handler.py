from rest_framework.views import exception_handler
from rest_framework.response import Response
import traceback
import logging

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    # Call REST framework's default exception handler first
    response = exception_handler(exc, context)

    # Log the full error for debugging
    if response is None:
        # This means DRF didn't handle it, so it's a 500 error
        logger.error(f"Unhandled exception: {exc}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        
        # Return a proper error response instead of generic 500
        return Response({
            'error': 'Internal server error',
            'detail': str(exc),
            'type': type(exc).__name__
        }, status=500)
    
    # Log handled exceptions too
    logger.warning(f"Exception: {exc} - Response: {response.data}")
    
    return response
