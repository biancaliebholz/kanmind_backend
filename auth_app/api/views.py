from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from auth_app.api.serializers import (
    EmailCheckSerializer,
    LoginSerializer,
    RegistrationSerializer,
    UserSerializer,
)
from auth_app.models import User


def build_auth_response(user, status_code):
    """Build the authentication response for a user."""
    token, _ = Token.objects.get_or_create(user=user)
    data = {
        "token": token.key,
        "fullname": user.fullname,
        "email": user.email,
        "user_id": user.id,
    }
    return Response(data, status=status_code)


class RegistrationView(CreateAPIView):
    """Handle user registration requests."""

    queryset = User.objects.all()
    serializer_class = RegistrationSerializer

    def create(self, request, *args, **kwargs):
        """Create a user and return authentication data."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        return build_auth_response(
            user,
            status.HTTP_201_CREATED,
        )


class LoginView(APIView):
    """Handle user login requests."""

    def post(self, request):
        """Authenticate a user and return authentication data."""
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]

        return build_auth_response(
            user,
            status.HTTP_200_OK,
        )


class EmailCheckView(APIView):
    """Handle authenticated email lookup requests."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Return user data for a registered email address."""
        serializer = EmailCheckSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        user = self.get_user(serializer.validated_data["email"])
        if user is None:
            return self.email_not_found_response()

        return Response(
            UserSerializer(user).data,
            status=status.HTTP_200_OK,
        )

    def get_user(self, email):
        """Return the user matching the given email address."""
        try:
            return User.objects.get(email=email)
        except User.DoesNotExist:
            return None

    def email_not_found_response(self):
        """Return a response for an unknown email address."""
        return Response(
            {"detail": "Email not found."},
            status=status.HTTP_404_NOT_FOUND,
        )
