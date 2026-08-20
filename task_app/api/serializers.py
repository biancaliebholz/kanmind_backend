from rest_framework import serializers

from auth_app.models import User
from task_app.models import Comment, Task


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "fullname",
        ]


class TaskSerializer(serializers.ModelSerializer):
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
        return obj.comments.count()

    def validate(self, attrs):
        board = attrs.get("board", self._current_value("board"))
        assignee = attrs.get("assignee", self._current_value("assignee"))
        reviewer = attrs.get("reviewer", self._current_value("reviewer"))

        self.validate_board_member(board, assignee, "assignee_id")
        self.validate_board_member(board, reviewer, "reviewer_id")
        return attrs

    def _current_value(self, field_name):
        if self.instance is None:
            return None

        return getattr(self.instance, field_name, None)

    def validate_board_member(self, board, user, field_name):
        if user is None:
            return

        if not board.members.filter(id=user.id).exists():
            raise serializers.ValidationError(
                {field_name: "User must be a member of the board."}
            )

    def create(self, validated_data):
        request = self.context["request"]

        return Task.objects.create(
            created_by=request.user,
            **validated_data,
        )

    def update(self, instance, validated_data):
        validated_data.pop("board", None)

        return super().update(
            instance,
            validated_data,
        )


class TaskUpdateSerializer(TaskSerializer):
    class Meta(TaskSerializer.Meta):
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
    author = serializers.CharField(
        source="author.fullname",
        read_only=True,
    )

    class Meta:
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
