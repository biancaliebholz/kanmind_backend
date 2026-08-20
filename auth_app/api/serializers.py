from django.contrib.auth import authenticate
from rest_framework import serializers

from auth_app.models import User


class RegistrationSerializer(serializers.ModelSerializer):
    """Validate and create new user registrations."""

    password = serializers.CharField(write_only=True)
    repeated_password = serializers.CharField(write_only=True)

    class Meta:
        """Configure fields for user registration."""

        model = User
        fields = [
            "fullname",
            "email",
            "password",
            "repeated_password",
        ]

    def validate(self, attrs):
        """Validate that both submitted passwords match."""
        if attrs["password"] != attrs["repeated_password"]:
            raise serializers.ValidationError(
                {"password": "Passwords do not match."}
            )

        return attrs

    def create(self, validated_data):
        """Create a user from validated registration data."""
        validated_data.pop("repeated_password")

        user = User.objects.create_user(**validated_data)
        return user


class LoginSerializer(serializers.Serializer):
    """Validate user credentials for authentication."""

    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        """Authenticate a user with email and password."""
        user = authenticate(
            email=attrs["email"],
            password=attrs["password"],
        )

        if user is None:
            raise serializers.ValidationError(
                "Invalid email or password."
            )

        attrs["user"] = user
        return attrs


class EmailCheckSerializer(serializers.Serializer):
    """Validate email input for user lookup."""

    email = serializers.EmailField()


class UserSerializer(serializers.ModelSerializer):
    """Serialize basic user information."""

    class Meta:
        """Configure fields exposed for a user."""

        model = User
        fields = [
            "id",
            "email",
            "fullname",
        ]
