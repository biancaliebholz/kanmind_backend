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
    queryset = Task.objects.all()
    permission_classes = [IsAuthenticated]
    http_method_names = [
        "post",
        "patch",
        "delete",
    ]

    def get_serializer_class(self):
        if self.action == "partial_update":
            return TaskUpdateSerializer

        return TaskSerializer

    def get_permissions(self):
        if self.action == "destroy":
            permission_classes = [
                IsAuthenticated,
                CanDeleteTask,
            ]

        elif self.action == "partial_update":
            permission_classes = [
                IsAuthenticated,
                IsTaskBoardMember,
            ]

        else:
            permission_classes = [
                IsAuthenticated,
            ]

        return [
            permission()
            for permission in permission_classes
        ]

    def create(self, request, *args, **kwargs):
        board_id = request.data.get("board")

        try:
            board = Board.objects.get(id=board_id)
        except Board.DoesNotExist:
            return Response(
                {"detail": "Board not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        is_member = (
            board.owner == request.user
            or board.members.filter(id=request.user.id).exists()
        )

        if not is_member:
            return Response(
                {
                    "detail":
                        "You must be a member of the board."
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = self.get_serializer(
            data=request.data,
        )
        serializer.is_valid(raise_exception=True)
        task = serializer.save()

        response_serializer = TaskSerializer(task)

        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED,
        )

    def destroy(self, request, *args, **kwargs):
        task = self.get_object()
        task.delete()

        return Response(
            status=status.HTTP_204_NO_CONTENT,
        )


class AssignedToMeView(ListAPIView):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Task.objects.filter(
            assignee=self.request.user
        )


class ReviewingView(ListAPIView):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Task.objects.filter(
            reviewer=self.request.user
        )


class CommentListCreateView(ListCreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

    def get_task(self):
        try:
            return Task.objects.get(
                id=self.kwargs["task_id"]
            )
        except Task.DoesNotExist:
            return None

    def check_board_permission(self, task):
        user = self.request.user

        return (
            task.board.owner == user
            or task.board.members.filter(id=user.id).exists()
        )

    def get_queryset(self):
        task = self.get_task()

        if task is None:
            return Comment.objects.none()

        return task.comments.order_by("created_at")

    def list(self, request, *args, **kwargs):
        task = self.get_task()

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

        return super().list(
            request,
            *args,
            **kwargs,
        )

    def create(self, request, *args, **kwargs):
        task = self.get_task()

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

        serializer = self.get_serializer(
            data=request.data,
        )
        serializer.is_valid(raise_exception=True)

        comment = serializer.save(
            task=task,
            author=request.user,
        )

        return Response(
            CommentSerializer(comment).data,
            status=status.HTTP_201_CREATED,
        )


class CommentDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(
        self,
        request,
        task_id,
        comment_id,
    ):
        try:
            comment = Comment.objects.get(
                id=comment_id,
                task_id=task_id,
            )
        except Comment.DoesNotExist:
            return Response(
                {"detail": "Comment not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        permission = IsCommentAuthor()

        if not permission.has_object_permission(
            request,
            self,
            comment,
        ):
            return Response(
                {
                    "detail":
                        "Only the comment author can delete this comment."
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        comment.delete()

        return Response(
            status=status.HTTP_204_NO_CONTENT,
        )
