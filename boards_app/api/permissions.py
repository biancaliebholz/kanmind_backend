from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsBoardMemberOrOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return (
                obj.owner == request.user
                or obj.members.filter(id=request.user.id).exists()
            )

        if request.method == "DELETE":
            return obj.owner == request.user

        return (
            obj.owner == request.user
            or obj.members.filter(id=request.user.id).exists()
        )