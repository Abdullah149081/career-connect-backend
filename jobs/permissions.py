from rest_framework import permissions


class IsEmployer(permissions.BasePermission):
    """Permission to check if user is an employer."""

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.user_type == "employer"


class IsJobSeeker(permissions.BasePermission):
    """Permission to check if user is a job seeker."""

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.user_type == "job_seeker"


class IsOwnerOrReadOnly(permissions.BasePermission):
    """Permission to only allow owners to edit their objects."""

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        # Check if the user is the owner
        if hasattr(obj, "employer"):
            return obj.employer == request.user
        elif hasattr(obj, "user"):
            return obj.user == request.user
        elif hasattr(obj, "applicant"):
            return obj.applicant == request.user

        return False
