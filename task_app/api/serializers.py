from rest_framework import serializers

from auth_app.models import User
from task_app.models import Comment, Task


class UserSerializer(serializers.ModelSerializer):
    """Serialize basic user information."""

    class Meta:
        """Configure fields exposed for a user."""

        model = User
        fields = [
            "id",
            "email",
            "fullname",
        ]


class TaskSerializer(serializers.ModelSerializer):
    """Validate and serialize task data."""

    assignee = UserSerializer(read_only=True)
    reviewer = UserSerializer(read_only=True)

    assignee_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source="assignee",
        write_only=True,
        required=False,
        allow_null=True,
    )

    reviewer_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source="reviewer",
        write_only=True,
        required=False,
        allow_null=True,
    )

    comments_count = serializers.SerializerMethodField()

    class Meta:
        """Configure fields used for task serialization."""

        model = Task
        fields = [
            "id",
            "board",
            "title",
            "description",
            "status",
            "priority",
            "assignee_id",
            "reviewer_id",
            "assignee",
            "reviewer",
            "due_date",
            "comments_count",
        ]

    def get_comments_count(self, obj):
        """Return the number of comments on a task."""
        return obj.comments.count()

    def validate(self, attrs):
        """Validate assignee and reviewer board membership."""
        board = attrs.get("board", self._current_value("board"))
        assignee = attrs.get("assignee", self._current_value("assignee"))
        reviewer = attrs.get("reviewer", self._current_value("reviewer"))

        self.validate_board_member(board, assignee, "assignee_id")
        self.validate_board_member(board, reviewer, "reviewer_id")
        return attrs

    def _current_value(self, field_name):
        """Return the current field value during task updates."""
        if self.instance is None:
            return None

        return getattr(self.instance, field_name, None)

    def validate_board_member(self, board, user, field_name):
        """Validate that a selected user belongs to the board."""
        if user is None:
            return

        if not board.members.filter(id=user.id).exists():
            raise serializers.ValidationError(
                {field_name: "User must be a member of the board."}
            )

    def create(self, validated_data):
        """Create a task and store its creator."""
        request = self.context["request"]

        return Task.objects.create(
            created_by=request.user,
            **validated_data,
        )

    def update(self, instance, validated_data):
        """Update task fields without allowing board changes."""
        validated_data.pop("board", None)

        return super().update(
            instance,
            validated_data,
        )


class TaskUpdateSerializer(TaskSerializer):
    """Serialize fields allowed during task updates."""

    class Meta(TaskSerializer.Meta):
        """Configure fields accepted for task updates."""

        fields = [
            "id",
            "title",
            "description",
            "status",
            "priority",
            "assignee_id",
            "reviewer_id",
            "assignee",
            "reviewer",
            "due_date",
        ]


class CommentSerializer(serializers.ModelSerializer):
    """Validate and serialize task comments."""

    author = serializers.CharField(
        source="author.fullname",
        read_only=True,
    )

    class Meta:
        """Configure fields exposed for comments."""

        model = Comment
        fields = [
            "id",
            "created_at",
            "author",
            "content",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "author",
        ]
