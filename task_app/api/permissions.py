from rest_framework.permissions import BasePermission


class IsTaskBoardMember(BasePermission):
    def has_object_permission(self, request, view, obj):
        board = obj.board

        return (
            board.owner == request.user
            or board.members.filter(id=request.user.id).exists()
        )


class CanDeleteTask(BasePermission):
    def has_object_permission(self, request, view, obj):
        return (
            obj.created_by == request.user
            or obj.board.owner == request.user
        )


class IsCommentAuthor(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.author == request.user