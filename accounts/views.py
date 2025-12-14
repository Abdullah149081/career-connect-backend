from rest_framework import generics, status, permissions, serializers, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model
from .serializers import (
    UserRegistrationSerializer,
    UserSerializer,
    EmailVerificationSerializer,
)

User = get_user_model()


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        # Check if user is verified
        try:
            user = User.objects.get(email=attrs["email"])
            if not user.is_verified:
                raise serializers.ValidationError(
                    "Email not verified. Please check your email for verification link."
                )
        except User.DoesNotExist:
            pass

        data = super().validate(attrs)
        data["user_type"] = self.user.user_type
        data["email"] = self.user.email
        data["first_name"] = self.user.first_name
        data["last_name"] = self.user.last_name

        return data


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class UserRegistrationView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        return Response(
            {
                "message": "Registration successful! Please check your email to verify your account.",
                "user": UserSerializer(user).data,
            },
            status=status.HTTP_201_CREATED,
        )


class EmailVerificationView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = EmailVerificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        token = serializer.validated_data["token"]

        try:
            user = User.objects.get(verification_token=token)
            if user.is_verified:
                return Response(
                    {"message": "Email already verified."}, status=status.HTTP_200_OK
                )

            user.is_verified = True
            user.is_active = True
            user.save()

            return Response(
                {"message": "Email verified successfully! You can now log in."},
                status=status.HTTP_200_OK,
            )
        except User.DoesNotExist:
            return Response(
                {"error": "Invalid verification token."},
                status=status.HTTP_400_BAD_REQUEST,
            )


class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class UserProfileViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for user profiles (read-only)."""

    queryset = User.objects.filter(is_active=True, is_verified=True)
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Allow users to only see their own profile or public employer profiles
        if self.request.user.user_type == "job_seeker":
            return User.objects.filter(id=self.request.user.id)
        return User.objects.filter(is_active=True, is_verified=True)
