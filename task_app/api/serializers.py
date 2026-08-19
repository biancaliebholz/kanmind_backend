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
        board = attrs.get(
            "board",
            getattr(self.instance, "board", None),
        )

        assignee = attrs.get(
            "assignee",
            getattr(self.instance, "assignee", None),
        )

        reviewer = attrs.get(
            "reviewer",
            getattr(self.instance, "reviewer", None),
        )

        if assignee is not None:
            if not board.members.filter(id=assignee.id).exists():
                raise serializers.ValidationError(
                    {
                        "assignee_id":
                            "Assignee must be a member of the board."
                    }
                )

        if reviewer is not None:
            if not board.members.filter(id=reviewer.id).exists():
                raise serializers.ValidationError(
                    {
                        "reviewer_id":
                            "Reviewer must be a member of the board."
                    }
                )

        return attrs

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