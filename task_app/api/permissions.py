from rest_framework.permissions import BasePermission


class IsTaskBoardMember(BasePermission):
    """Allow task access to the board owner or its members."""

    def has_object_permission(self, request, view, obj):
        """Check whether the user belongs to the task board."""
        board = obj.board

        return (
            board.owner == request.user
            or board.members.filter(id=request.user.id).exists()
        )


class CanDeleteTask(BasePermission):
    """Control permission to delete a task."""

    def has_object_permission(self, request, view, obj):
        """Allow deletion by the task creator or board owner."""
        return (
            obj.created_by == request.user
            or obj.board.owner == request.user
        )


class IsCommentAuthor(BasePermission):
    """Control permission to modify a comment."""

    def has_object_permission(self, request, view, obj):
        """Allow access only to the comment author."""
        return obj.author == request.user
