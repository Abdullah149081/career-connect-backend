from django.contrib import admin
from .models import JobCategory, JobListing, JobApplication, Resume, EmployerReview


@admin.register(JobCategory)
class JobCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "created_at")
    search_fields = ("name",)


@admin.register(JobListing)
class JobListingAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "employer",
        "category",
        "location",
        "employment_type",
        "is_active",
        "created_at",
    )
    list_filter = ("category", "employment_type", "is_active", "created_at")
    search_fields = (
        "title",
        "description",
        "employer__email",
        "employer__company_name",
    )
    date_hierarchy = "created_at"


@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    list_display = ("applicant", "job", "status", "applied_at")
    list_filter = ("status", "applied_at")
    search_fields = ("applicant__email", "job__title")
    date_hierarchy = "applied_at"


@admin.register(Resume)
class ResumeAdmin(admin.ModelAdmin):
    list_display = ("user", "title", "is_primary", "uploaded_at")
    list_filter = ("is_primary", "uploaded_at")
    search_fields = ("user__email", "title")


@admin.register(EmployerReview)
class EmployerReviewAdmin(admin.ModelAdmin):
    list_display = ("employer", "reviewer", "rating", "created_at")
    list_filter = ("rating", "created_at")
    search_fields = ("employer__email", "employer__company_name", "reviewer__email")
    date_hierarchy = "created_at"
