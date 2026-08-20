from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsBoardMemberOrOwner(BasePermission):
    """Control board access for owners and board members."""

    def has_object_permission(self, request, view, obj):
        """Check whether the user may access or modify the board."""
        is_owner = obj.owner == request.user
        is_member = obj.members.filter(id=request.user.id).exists()

        if request.method in SAFE_METHODS:
            return is_owner or is_member

        if request.method == "DELETE":
            return is_owner

        return is_owner or is_member
