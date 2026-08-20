from django.db.models import Q
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from boards_app.api.permissions import IsBoardMemberOrOwner
from boards_app.api.serializers import (
    BoardCreateSerializer,
    BoardDetailSerializer,
    BoardListSerializer,
    BoardUpdateSerializer,
)
from boards_app.models import Board


class BoardViewSet(ModelViewSet):
    """Handle board CRUD operations and board access."""

    permission_classes = [
        IsAuthenticated,
        IsBoardMemberOrOwner,
    ]

    def get_queryset(self):
        """Return boards accessible to the current user."""
        user = self.request.user

        if self.action == "list":
            return Board.objects.filter(
                Q(owner=user) | Q(members=user)
            ).distinct()

        return Board.objects.all()

    def get_serializer_class(self):
        """Return the serializer for the current board action."""
        serializer_map = {
            "list": BoardListSerializer,
            "create": BoardCreateSerializer,
            "retrieve": BoardDetailSerializer,
            "update": BoardUpdateSerializer,
            "partial_update": BoardUpdateSerializer,
        }
        return serializer_map.get(self.action, BoardListSerializer)

    def create(self, request, *args, **kwargs):
        """Create a board and return its serialized data."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        board = serializer.save()

        response_serializer = BoardListSerializer(board)

        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED,
        )

    def destroy(self, request, *args, **kwargs):
        """Delete a board and return an empty response."""
        board = self.get_object()

        board.delete()

        return Response(
            status=status.HTTP_204_NO_CONTENT,
        )
