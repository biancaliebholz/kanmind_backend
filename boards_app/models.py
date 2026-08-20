from django.conf import settings
from django.db import models


class Board(models.Model):
    """Represent a KanMind board with an owner and members."""

    title = models.CharField(max_length=255)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="owned_boards",
    )
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="member_boards",
    )

    def __str__(self):
        """Return the board title as its string representation."""
        return self.title
