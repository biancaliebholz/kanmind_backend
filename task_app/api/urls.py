from django.urls import path
from rest_framework.routers import DefaultRouter

from task_app.api.views import (
    AssignedToMeView,
    CommentDeleteView,
    CommentListCreateView,
    ReviewingView,
    TaskViewSet,
)


router = DefaultRouter()

router.register(
    "tasks",
    TaskViewSet,
    basename="task",
)


urlpatterns = [
    path(
        "tasks/assigned-to-me/",
        AssignedToMeView.as_view(),
        name="assigned-to-me",
    ),
    path(
        "tasks/reviewing/",
        ReviewingView.as_view(),
        name="reviewing",
    ),
    path(
        "tasks/<int:task_id>/comments/",
        CommentListCreateView.as_view(),
        name="task-comments",
    ),
    path(
        "tasks/<int:task_id>/comments/<int:comment_id>/",
        CommentDeleteView.as_view(),
        name="comment-delete",
    ),
]

urlpatterns += router.urls