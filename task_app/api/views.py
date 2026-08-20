from rest_framework import status
from rest_framework.generics import (
    ListAPIView,
    ListCreateAPIView,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from boards_app.models import Board
from task_app.api.permissions import (
    CanDeleteTask,
    IsCommentAuthor,
    IsTaskBoardMember,
)
from task_app.api.serializers import (
    CommentSerializer,
    TaskSerializer,
    TaskUpdateSerializer,
)
from task_app.models import Comment, Task


class TaskViewSet(ModelViewSet):
    """Handle creation, updates, and deletion of tasks."""

    queryset = Task.objects.all()
    permission_classes = [IsAuthenticated]
    http_method_names = [
        "post",
        "patch",
        "delete",
    ]

    def get_serializer_class(self):
        """Return the serializer for the current task action."""
        if self.action == "partial_update":
            return TaskUpdateSerializer
        return TaskSerializer

    def get_permissions(self):
        """Return permissions required for the current task action."""
        permission_map = {
            "destroy": [IsAuthenticated, CanDeleteTask],
            "partial_update": [IsAuthenticated, IsTaskBoardMember],
        }
        permission_classes = permission_map.get(
            self.action,
            [IsAuthenticated],
        )
        return [permission() for permission in permission_classes]

    def create(self, request, *args, **kwargs):
        """Create a task when the user may access its board."""
        board = self.get_board(request.data.get("board"))
        if board is None:
            return self.board_not_found_response()
        if not self.user_can_access_board(board, request.user):
            return self.board_permission_denied_response()

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        task = serializer.save()
        return self.created_task_response(task)

    def get_board(self, board_id):
        """Return a board by ID or None when it does not exist."""
        try:
            return Board.objects.get(id=board_id)
        except Board.DoesNotExist:
            return None

    def user_can_access_board(self, board, user):
        """Check whether a user owns or belongs to a board."""
        return (
            board.owner == user
            or board.members.filter(id=user.id).exists()
        )

    def board_not_found_response(self):
        """Return a response when the requested board is missing."""
        return Response(
            {"detail": "Board not found."},
            status=status.HTTP_404_NOT_FOUND,
        )

    def board_permission_denied_response(self):
        """Return a response when board access is not permitted."""
        return Response(
            {"detail": "You must be a member of the board."},
            status=status.HTTP_403_FORBIDDEN,
        )

    def created_task_response(self, task):
        """Return the response for a successfully created task."""
        serializer = TaskSerializer(task)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
        )

    def destroy(self, request, *args, **kwargs):
        """Delete a task and return an empty response."""
        task = self.get_object()
        task.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class AssignedToMeView(ListAPIView):
    """List tasks assigned to the authenticated user."""

    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Return tasks assigned to the current user."""
        return Task.objects.filter(
            assignee=self.request.user
        )


class ReviewingView(ListAPIView):
    """List tasks reviewed by the authenticated user."""

    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Return tasks reviewed by the current user."""
        return Task.objects.filter(
            reviewer=self.request.user
        )


class CommentListCreateView(ListCreateAPIView):
    """Handle listing and creation of task comments."""

    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

    def get_task(self):
        """Return the task from the current URL or None."""
        try:
            return Task.objects.get(id=self.kwargs["task_id"])
        except Task.DoesNotExist:
            return None

    def check_board_permission(self, task):
        """Check whether the user may access the task board."""
        user = self.request.user
        return (
            task.board.owner == user
            or task.board.members.filter(id=user.id).exists()
        )

    def get_queryset(self):
        """Return comments for the current task chronologically."""
        task = self.get_task()
        if task is None:
            return Comment.objects.none()
        return task.comments.order_by("created_at")

    def list(self, request, *args, **kwargs):
        """Return comments when the task is accessible."""
        task = self.get_task()
        error_response = self.get_task_access_error(task)
        if error_response:
            return error_response
        return super().list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        """Create a comment for an accessible task."""
        task = self.get_task()
        error_response = self.get_task_access_error(task)
        if error_response:
            return error_response

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        comment = serializer.save(task=task, author=request.user)
        return self.created_comment_response(comment)

    def get_task_access_error(self, task):
        """Return an error response when task access is invalid."""
        if task is None:
            return Response(
                {"detail": "Task not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        if not self.check_board_permission(task):
            return Response(
                {"detail": "Permission denied."},
                status=status.HTTP_403_FORBIDDEN,
            )
        return None

    def created_comment_response(self, comment):
        """Return the response for a newly created comment."""
        return Response(
            CommentSerializer(comment).data,
            status=status.HTTP_201_CREATED,
        )


class CommentDeleteView(APIView):
    """Handle deletion of individual task comments."""

    permission_classes = [IsAuthenticated]

    def delete(self, request, task_id, comment_id):
        """Delete a comment when the user is its author."""
        comment = self.get_comment(task_id, comment_id)
        if comment is None:
            return self.comment_not_found_response()
        if not self.is_comment_author(request, comment):
            return self.permission_denied_response()

        comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def get_comment(self, task_id, comment_id):
        """Return a comment belonging to the specified task."""
        try:
            return Comment.objects.get(
                id=comment_id,
                task_id=task_id,
            )
        except Comment.DoesNotExist:
            return None

    def is_comment_author(self, request, comment):
        """Check whether the current user authored the comment."""
        permission = IsCommentAuthor()
        return permission.has_object_permission(
            request,
            self,
            comment,
        )

    def comment_not_found_response(self):
        """Return a response when the comment does not exist."""
        return Response(
            {"detail": "Comment not found."},
            status=status.HTTP_404_NOT_FOUND,
        )

    def permission_denied_response(self):
        """Return a response when comment deletion is forbidden."""
        return Response(
            {
                "detail":
                    "Only the comment author can delete this comment."
            },
            status=status.HTTP_403_FORBIDDEN,
        )
