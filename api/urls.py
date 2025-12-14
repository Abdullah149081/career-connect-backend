from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers as nested_routers
from rest_framework_simplejwt.views import TokenRefreshView

# Import job-related views
from jobs.views import (
    JobListingViewSet,
    JobApplicationViewSet,
    JobCategoryViewSet,
    EmployerReviewViewSet,
    ResumeViewSet,
    DashboardView,
)

# Import account-related views
from accounts.views import (
    UserProfileViewSet,
    UserRegistrationView,
    EmailVerificationView,
    CustomTokenObtainPairView,
    UserProfileView,
    LogoutView,
)

# Create main router
router = DefaultRouter()

# Register job-related viewsets
router.register("jobs", JobListingViewSet, basename="jobs")
router.register("categories", JobCategoryViewSet, basename="categories")
router.register("applications", JobApplicationViewSet, basename="applications")
router.register("resumes", ResumeViewSet, basename="resumes")
router.register("profiles", UserProfileViewSet, basename="profiles")

# Create nested router for job-specific reviews
job_router = nested_routers.NestedDefaultRouter(router, "jobs", lookup="job")
job_router.register("reviews", EmployerReviewViewSet, basename="job-reviews")

urlpatterns = [
    # Include all router URLs
    path("", include(router.urls)),
    path("", include(job_router.urls)),
    # Dashboard endpoint
    path("dashboard/", DashboardView.as_view(), name="dashboard"),
    # Custom account endpoints
    path("accounts/register/", UserRegistrationView.as_view(), name="user-register"),
    path(
        "accounts/verify-email/", EmailVerificationView.as_view(), name="verify-email"
    ),
    path("accounts/login/", CustomTokenObtainPairView.as_view(), name="token-obtain"),
    path("accounts/logout/", LogoutView.as_view(), name="logout"),
    path("accounts/token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("accounts/profile/", UserProfileView.as_view(), name="user-profile"),
    # Djoser authentication endpoints (alternative authentication method)
    path("auth/", include("djoser.urls")),
    path("auth/", include("djoser.urls.jwt")),
]
