from django.urls import path

from auth_app.api.views import (
    EmailCheckView,
    LoginView,
    RegistrationView,
)


urlpatterns = [
    path(
        "registration/",
        RegistrationView.as_view(),
        name="registration",
    ),
    path(
        "login/",
        LoginView.as_view(),
        name="login",
    ),
    path(
        "email-check/",
        EmailCheckView.as_view(),
        name="email-check",
    ),
]
