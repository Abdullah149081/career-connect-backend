from rest_framework import viewsets, generics, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db.models import Count, Q
from .models import JobCategory, JobListing, JobApplication, Resume, EmployerReview
from .serializers import (
    JobCategorySerializer,
    JobListingSerializer,
    JobApplicationSerializer,
    ApplicationStatusUpdateSerializer,
    ResumeSerializer,
    EmployerReviewSerializer,
)
from .permissions import IsEmployer, IsJobSeeker, IsOwnerOrReadOnly
from .filters import JobListingFilter


class JobCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for job categories."""

    queryset = JobCategory.objects.annotate(
        job_count=Count("jobs", filter=Q(jobs__is_active=True))
    )
    serializer_class = JobCategorySerializer
    permission_classes = [permissions.AllowAny]


class JobListingViewSet(viewsets.ModelViewSet):
    """ViewSet for job listings."""

    queryset = JobListing.objects.filter(is_active=True).select_related(
        "employer", "category"
    )
    serializer_class = JobListingSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = JobListingFilter
    search_fields = ["title", "description", "requirements", "location"]
    ordering_fields = ["created_at", "title", "salary_min"]
    ordering = ["-created_at"]

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            permission_classes = [IsEmployer, IsOwnerOrReadOnly]
        elif self.action in ["my_listings"]:
            permission_classes = [IsEmployer]
        else:
            permission_classes = [permissions.AllowAny]
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        serializer.save(employer=self.request.user)

    @action(detail=False, methods=["get"], permission_classes=[IsEmployer])
    def my_listings(self, request):
        """Get all job listings created by the current employer."""
        listings = JobListing.objects.filter(employer=request.user).select_related(
            "category"
        )
        page = self.paginate_queryset(listings)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(listings, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"], permission_classes=[IsEmployer])
    def applications(self, request, pk=None):
        """Get all applications for a specific job listing."""
        job = self.get_object()
        if job.employer != request.user:
            return Response(
                {"error": "You do not have permission to view these applications."},
                status=status.HTTP_403_FORBIDDEN,
            )

        applications = job.applications.all().select_related("applicant")
        serializer = JobApplicationSerializer(applications, many=True)
        return Response(serializer.data)


class JobApplicationViewSet(viewsets.ModelViewSet):
    """ViewSet for job applications."""

    queryset = JobApplication.objects.all().select_related("job", "applicant")
    serializer_class = JobApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ["status"]
    ordering_fields = ["applied_at"]
    ordering = ["-applied_at"]

    def get_queryset(self):
        user = self.request.user
        if user.user_type == "job_seeker":
            # Job seekers see their own applications
            return JobApplication.objects.filter(applicant=user).select_related(
                "job", "job__employer"
            )
        elif user.user_type == "employer":
            # Employers see applications for their jobs
            return JobApplication.objects.filter(job__employer=user).select_related(
                "applicant", "job"
            )
        return JobApplication.objects.none()

    def perform_create(self, serializer):
        serializer.save(applicant=self.request.user)

    @action(detail=True, methods=["patch"], permission_classes=[IsEmployer])
    def update_status(self, request, pk=None):
        """Allow employers to update application status."""
        application = self.get_object()

        # Verify the employer owns the job
        if application.job.employer != request.user:
            return Response(
                {"error": "You do not have permission to update this application."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = ApplicationStatusUpdateSerializer(
            application, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(JobApplicationSerializer(application).data)

    @action(detail=False, methods=["get"], permission_classes=[IsJobSeeker])
    def my_applications(self, request):
        """Get all applications submitted by the current job seeker."""
        applications = JobApplication.objects.filter(
            applicant=request.user
        ).select_related("job", "job__employer")
        page = self.paginate_queryset(applications)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(applications, many=True)
        return Response(serializer.data)


class ResumeViewSet(viewsets.ModelViewSet):
    """ViewSet for resume management."""

    queryset = Resume.objects.all()
    serializer_class = ResumeSerializer
    permission_classes = [IsJobSeeker]

    def get_queryset(self):
        return Resume.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=["post"])
    def set_primary(self, request, pk=None):
        """Set a resume as primary."""
        resume = self.get_object()
        Resume.objects.filter(user=request.user, is_primary=True).update(
            is_primary=False
        )
        resume.is_primary = True
        resume.save()
        return Response({"message": "Resume set as primary."})


class EmployerReviewViewSet(viewsets.ModelViewSet):
    """ViewSet for employer reviews."""

    queryset = EmployerReview.objects.all().select_related("employer", "reviewer")
    serializer_class = EmployerReviewSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ["employer", "rating"]
    ordering_fields = ["created_at", "rating"]
    ordering = ["-created_at"]

    def get_permissions(self):
        if self.action in ["create"]:
            permission_classes = [IsJobSeeker]
        elif self.action in ["update", "partial_update", "destroy"]:
            permission_classes = [IsJobSeeker, IsOwnerOrReadOnly]
        else:
            permission_classes = [permissions.AllowAny]
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        serializer.save(reviewer=self.request.user)


class DashboardView(generics.GenericAPIView):
    """Dashboard view for different user types."""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user

        if user.user_type == "employer":
            # Employer dashboard data
            total_jobs = JobListing.objects.filter(employer=user).count()
            active_jobs = JobListing.objects.filter(
                employer=user, is_active=True
            ).count()
            total_applications = JobApplication.objects.filter(
                job__employer=user
            ).count()
            pending_applications = JobApplication.objects.filter(
                job__employer=user, status="pending"
            ).count()

            recent_jobs = JobListing.objects.filter(employer=user).order_by(
                "-created_at"
            )[:5]
            recent_applications = JobApplication.objects.filter(
                job__employer=user
            ).order_by("-applied_at")[:10]

            data = {
                "user_type": "employer",
                "stats": {
                    "total_jobs": total_jobs,
                    "active_jobs": active_jobs,
                    "total_applications": total_applications,
                    "pending_applications": pending_applications,
                },
                "recent_jobs": JobListingSerializer(recent_jobs, many=True).data,
                "recent_applications": JobApplicationSerializer(
                    recent_applications, many=True
                ).data,
            }

        elif user.user_type == "job_seeker":
            # Job seeker dashboard data
            total_applications = JobApplication.objects.filter(applicant=user).count()
            pending_applications = JobApplication.objects.filter(
                applicant=user, status="pending"
            ).count()
            accepted_applications = JobApplication.objects.filter(
                applicant=user, status="accepted"
            ).count()
            total_resumes = Resume.objects.filter(user=user).count()

            recent_applications = JobApplication.objects.filter(
                applicant=user
            ).order_by("-applied_at")[:10]
            resumes = Resume.objects.filter(user=user).order_by("-uploaded_at")[:5]

            data = {
                "user_type": "job_seeker",
                "stats": {
                    "total_applications": total_applications,
                    "pending_applications": pending_applications,
                    "accepted_applications": accepted_applications,
                    "total_resumes": total_resumes,
                },
                "recent_applications": JobApplicationSerializer(
                    recent_applications, many=True
                ).data,
                "resumes": ResumeSerializer(resumes, many=True).data,
            }
        else:
            return Response(
                {"error": "Invalid user type."}, status=status.HTTP_400_BAD_REQUEST
            )

        return Response(data)
