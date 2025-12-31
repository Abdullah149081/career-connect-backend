from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from cloudinary_storage.storage import MediaCloudinaryStorage

User = get_user_model()


class JobCategory(models.Model):
    """Job categories like IT, Healthcare, Finance, etc."""

    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Job Categories"
        ordering = ["name"]


class JobListing(models.Model):
    """Job postings created by employers."""

    EMPLOYMENT_TYPE_CHOICES = (
        ("full_time", "Full Time"),
        ("part_time", "Part Time"),
        ("contract", "Contract"),
        ("internship", "Internship"),
        ("freelance", "Freelance"),
    )

    employer = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="job_listings"
    )
    title = models.CharField(max_length=255)
    description = models.TextField()
    requirements = models.TextField()
    location = models.CharField(max_length=255)
    category = models.ForeignKey(
        JobCategory, on_delete=models.SET_NULL, null=True, related_name="jobs"
    )
    employment_type = models.CharField(
        max_length=20, choices=EMPLOYMENT_TYPE_CHOICES, default="full_time"
    )
    salary_min = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    salary_max = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deadline = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.title} - {self.employer.company_name or self.employer.email}"

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["-created_at"]),
            models.Index(fields=["category"]),
            models.Index(fields=["employer"]),
        ]


class JobApplication(models.Model):
    """Job applications submitted by job seekers."""

    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("reviewed", "Reviewed"),
        ("accepted", "Accepted"),
        ("rejected", "Rejected"),
    )

    job = models.ForeignKey(
        JobListing, on_delete=models.CASCADE, related_name="applications"
    )
    applicant = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="job_applications"
    )
    resume = models.FileField(upload_to="resumes/%Y/%m/", storage=MediaCloudinaryStorage())
    cover_letter = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    applied_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.applicant.email} - {self.job.title}"

    class Meta:
        ordering = ["-applied_at"]
        unique_together = ["job", "applicant"]
        indexes = [
            models.Index(fields=["-applied_at"]),
            models.Index(fields=["status"]),
        ]


class Resume(models.Model):
    """Resume management for job seekers."""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="resumes")
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to="resumes/%Y/%m/", storage=MediaCloudinaryStorage())
    is_primary = models.BooleanField(default=False)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.email} - {self.title}"

    def save(self, *args, **kwargs):
        # If this resume is set as primary, remove primary from others
        if self.is_primary:
            Resume.objects.filter(user=self.user, is_primary=True).update(
                is_primary=False
            )
        super().save(*args, **kwargs)

    class Meta:
        ordering = ["-uploaded_at"]


class EmployerReview(models.Model):
    """Reviews for employers by job seekers."""

    employer = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="reviews_received"
    )
    reviewer = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="reviews_given"
    )
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Review for {self.employer.company_name} by {self.reviewer.email}"

    class Meta:
        ordering = ["-created_at"]
        unique_together = ["employer", "reviewer"]
