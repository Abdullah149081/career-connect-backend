from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from djoser.serializers import UserCreateSerializer as BaseUserCreateSerializer

User = get_user_model()


class UserCreateSerializer(BaseUserCreateSerializer):
    """Custom Djoser user creation serializer"""

    class Meta(BaseUserCreateSerializer.Meta):
        model = User
        fields = (
            "id",
            "email",
            "password",
            "first_name",
            "last_name",
            "user_type",
            "phone_number",
            "company_name",
            "bio",
        )

    def validate(self, attrs):
        attrs = super().validate(attrs)

        if attrs["user_type"] == "employer" and not attrs.get("company_name"):
            raise serializers.ValidationError(
                {"company_name": "Company name is required for employers."}
            )

        return attrs


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, required=True, style={"input_type": "password"}
    )
    password2 = serializers.CharField(
        write_only=True,
        required=True,
        style={"input_type": "password"},
        label="Confirm Password",
    )

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "password",
            "password2",
            "first_name",
            "last_name",
            "user_type",
            "phone_number",
            "company_name",
            "bio",
        )
        extra_kwargs = {
            "first_name": {"required": True},
            "last_name": {"required": True},
        }

    def validate(self, attrs):
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError(
                {"password": "Password fields didn't match."}
            )

        if attrs["user_type"] == "employer" and not attrs.get("company_name"):
            raise serializers.ValidationError(
                {"company_name": "Company name is required for employers."}
            )

        return attrs

    def create(self, validated_data):
        validated_data.pop("password2")
        password = validated_data.pop("password")
        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()

        # Send verification email
        self.send_verification_email(user)

        return user

    def send_verification_email(self, user):
        verification_url = (
            f"{settings.FRONTEND_URL}/verify-email/{user.verification_token}/"
        )
        subject = "Verify your CareerConnect account"
        message = f"""
        Hello {user.first_name},
        
        Thank you for registering at CareerConnect!
        
        Please click the link below to verify your email address:
        {verification_url}
        
        If you didn't create an account, please ignore this email.
        
        Best regards,
        CareerConnect Team
        """

        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "first_name",
            "last_name",
            "user_type",
            "phone_number",
            "company_name",
            "bio",
            "is_verified",
            "is_staff",
            "is_superuser",
            "date_joined",
        )
        read_only_fields = ("id", "email", "is_verified", "is_staff", "is_superuser", "date_joined")


class EmailVerificationSerializer(serializers.Serializer):
    token = serializers.UUIDField()
