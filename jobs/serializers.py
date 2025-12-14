from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import JobCategory, JobListing, JobApplication, Resume, EmployerReview
from django.core.mail import send_mail
from django.conf import settings

User = get_user_model()


class JobCategorySerializer(serializers.ModelSerializer):
    job_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = JobCategory
        fields = ("id", "name", "description", "job_count", "created_at")
        read_only_fields = ("id", "created_at", "job_count")


class EmployerBasicSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "email", "company_name", "first_name", "last_name")


class JobListingSerializer(serializers.ModelSerializer):
    employer_info = EmployerBasicSerializer(source="employer", read_only=True)
    category_name = serializers.CharField(source="category.name", read_only=True)
    application_count = serializers.SerializerMethodField()

    class Meta:
        model = JobListing
        fields = (
            "id",
            "employer",
            "employer_info",
            "title",
            "description",
            "requirements",
            "location",
            "category",
            "category_name",
            "employment_type",
            "salary_min",
            "salary_max",
            "is_active",
            "created_at",
            "updated_at",
            "deadline",
            "application_count",
        )
        read_only_fields = ("id", "employer", "created_at", "updated_at")

    def get_application_count(self, obj):
        return obj.applications.count()

    def validate(self, attrs):
        # Ensure only employers can create job listings
        request = self.context.get("request")
        if request and request.user.user_type != "employer":
            raise serializers.ValidationError("Only employers can create job listings.")
        return attrs


class JobApplicationSerializer(serializers.ModelSerializer):
    applicant_info = serializers.SerializerMethodField()
    job_title = serializers.CharField(source="job.title", read_only=True)

    class Meta:
        model = JobApplication
        fields = (
            "id",
            "job",
            "job_title",
            "applicant",
            "applicant_info",
            "resume",
            "cover_letter",
            "status",
            "applied_at",
            "updated_at",
        )
        read_only_fields = ("id", "applicant", "applied_at", "updated_at")

    def get_applicant_info(self, obj):
        return {
            "id": obj.applicant.id,
            "email": obj.applicant.email,
            "first_name": obj.applicant.first_name,
            "last_name": obj.applicant.last_name,
            "phone_number": obj.applicant.phone_number,
        }

    def validate(self, attrs):
        request = self.context.get("request")
        if request and request.user.user_type != "job_seeker":
            raise serializers.ValidationError("Only job seekers can apply for jobs.")

        # Check if already applied
        job = attrs.get("job")
        if JobApplication.objects.filter(job=job, applicant=request.user).exists():
            raise serializers.ValidationError("You have already applied for this job.")

        return attrs

    def create(self, validated_data):
        application = super().create(validated_data)

        # Send email to job seeker
        self.send_application_confirmation(application)

        # Send email to employer
        self.send_employer_notification(application)

        return application

    def send_application_confirmation(self, application):
        subject = f"Application Submitted: {application.job.title}"
        message = f"""
        Dear {application.applicant.first_name},
        
        Your application for the position of {application.job.title} at {application.job.employer.company_name or 'the company'} has been successfully submitted.
        
        Job Details:
        - Position: {application.job.title}
        - Location: {application.job.location}
        - Applied on: {application.applied_at.strftime('%B %d, %Y')}
        
        You will be notified when the employer reviews your application.
        
        Best regards,
        CareerConnect Team
        """

        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [application.applicant.email],
            fail_silently=True,
        )

    def send_employer_notification(self, application):
        subject = f"New Application: {application.job.title}"
        message = f"""
        Dear {application.job.employer.first_name},
        
        You have received a new application for your job posting: {application.job.title}
        
        Applicant Details:
        - Name: {application.applicant.first_name} {application.applicant.last_name}
        - Email: {application.applicant.email}
        - Applied on: {application.applied_at.strftime('%B %d, %Y')}
        
        Please log in to your dashboard to review the application.
        
        Best regards,
        CareerConnect Team
        """

        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [application.job.employer.email],
            fail_silently=True,
        )


class ApplicationStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobApplication
        fields = ("status",)


class ResumeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resume
        fields = (
            "id",
            "user",
            "title",
            "file",
            "is_primary",
            "uploaded_at",
            "updated_at",
        )
        read_only_fields = ("id", "user", "uploaded_at", "updated_at")


class EmployerReviewSerializer(serializers.ModelSerializer):
    reviewer_info = serializers.SerializerMethodField()
    employer_name = serializers.CharField(
        source="employer.company_name", read_only=True
    )

    class Meta:
        model = EmployerReview
        fields = (
            "id",
            "employer",
            "employer_name",
            "reviewer",
            "reviewer_info",
            "rating",
            "comment",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "reviewer", "created_at", "updated_at")

    def get_reviewer_info(self, obj):
        return {
            "first_name": obj.reviewer.first_name,
            "last_name": obj.reviewer.last_name,
        }

    def validate(self, attrs):
        request = self.context.get("request")
        employer = attrs.get("employer")

        if request and request.user.user_type != "job_seeker":
            raise serializers.ValidationError("Only job seekers can leave reviews.")

        if employer.user_type != "employer":
            raise serializers.ValidationError("Reviews can only be given to employers.")

        # Check if already reviewed
        if EmployerReview.objects.filter(
            employer=employer, reviewer=request.user
        ).exists():
            raise serializers.ValidationError(
                "You have already reviewed this employer."
            )

        return attrs
