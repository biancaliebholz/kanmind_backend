from rest_framework import serializers

from auth_app.models import User
from boards_app.models import Board
from task_app.models import Task


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


class BoardListSerializer(serializers.ModelSerializer):
    """Serialize boards for the board list view."""

    member_count = serializers.SerializerMethodField()
    ticket_count = serializers.SerializerMethodField()
    tasks_to_do_count = serializers.SerializerMethodField()
    tasks_high_prio_count = serializers.SerializerMethodField()

    class Meta:
        """Configure fields for the board list response."""

        model = Board
        fields = [
            "id",
            "title",
            "member_count",
            "ticket_count",
            "tasks_to_do_count",
            "tasks_high_prio_count",
            "owner_id",
        ]

    def get_member_count(self, obj):
        """Return the number of board members."""
        return obj.members.count()

    def get_ticket_count(self, obj):
        """Return the number of tasks on the board."""
        return obj.tasks.count()

    def get_tasks_to_do_count(self, obj):
        """Return the number of tasks with to-do status."""
        return obj.tasks.filter(status="to-do").count()

    def get_tasks_high_prio_count(self, obj):
        """Return the number of high-priority tasks."""
        return obj.tasks.filter(priority="high").count()


class BoardCreateSerializer(serializers.ModelSerializer):
    """Validate and create new boards."""

    members = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        many=True,
    )

    class Meta:
        """Configure fields accepted when creating a board."""

        model = Board
        fields = [
            "title",
            "members",
        ]

    def create(self, validated_data):
        """Create a board and assign its members."""
        members = validated_data.pop("members")
        request = self.context["request"]
        board = Board.objects.create(
            owner=request.user,
            **validated_data,
        )
        board.members.set(members)
        return board


class TaskSerializer(serializers.ModelSerializer):
    """Serialize tasks included in board details."""

    assignee = UserSerializer(read_only=True)
    reviewer = UserSerializer(read_only=True)
    comments_count = serializers.SerializerMethodField()

    class Meta:
        """Configure task fields shown inside board details."""

        model = Task
        fields = [
            "id",
            "title",
            "description",
            "status",
            "priority",
            "assignee",
            "reviewer",
            "due_date",
            "comments_count",
        ]

    def get_comments_count(self, obj):
        """Return the number of comments on a task."""
        return obj.comments.count()


class BoardDetailSerializer(serializers.ModelSerializer):
    """Serialize detailed board information."""

    members = UserSerializer(many=True, read_only=True)
    tasks = TaskSerializer(many=True, read_only=True)

    class Meta:
        """Configure fields for the board detail response."""

        model = Board
        fields = [
            "id",
            "title",
            "owner_id",
            "members",
            "tasks",
        ]


class BoardUpdateSerializer(serializers.ModelSerializer):
    """Validate board updates and serialize updated board data."""

    members = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        many=True,
        required=False,
        write_only=True,
    )

    owner_data = UserSerializer(
        source="owner",
        read_only=True,
    )

    members_data = UserSerializer(
        source="members",
        many=True,
        read_only=True,
    )

    class Meta:
        """Configure fields used when updating a board."""

        model = Board
        fields = [
            "id",
            "title",
            "members",
            "owner_data",
            "members_data",
        ]

    def update(self, instance, validated_data):
        """Update board fields and optionally replace members."""
        members = validated_data.pop("members", None)
        instance.title = validated_data.get(
            "title",
            instance.title,
        )
        instance.save()

        if members is not None:
            instance.members.set(members)
        return instance
