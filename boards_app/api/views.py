from django.db.models import Q
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from boards_app.api.serializers import (
    BoardCreateSerializer,
    BoardDetailSerializer,
    BoardListSerializer,
    BoardUpdateSerializer,
)
from boards_app.models import Board


class BoardViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        return Board.objects.filter(
            Q(owner=user) | Q(members=user)
        ).distinct()

    def get_serializer_class(self):
        if self.action == "list":
            return BoardListSerializer

        if self.action == "create":
            return BoardCreateSerializer

        if self.action == "retrieve":
            return BoardDetailSerializer

        if self.action in ["update", "partial_update"]:
            return BoardUpdateSerializer

        return BoardListSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        board = serializer.save()

        response_serializer = BoardListSerializer(board)

        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED,
        )

    def destroy(self, request, *args, **kwargs):
        board = self.get_object()

        if board.owner != request.user:
            return Response(
                {"detail": "Only the board owner can delete this board."},
                status=status.HTTP_403_FORBIDDEN,
            )

        board.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)