"""DRF serializers for the projects API."""

from rest_framework import serializers

from projects.models import Issue, Label, Project, Status, Workspace


class WorkspaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Workspace
        fields = [
            'id', 'name', 'slug', 'identifier_prefix', 'issue_counter',
            'description', 'icon', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'issue_counter', 'created_at', 'updated_at']


class StatusSerializer(serializers.ModelSerializer):
    project_id = serializers.PrimaryKeyRelatedField(
        source='project', read_only=True,
    )

    class Meta:
        model = Status
        fields = [
            'id', 'project_id', 'name', 'category', 'color',
            'sort_order', 'is_default', 'created_at',
        ]
        read_only_fields = ['id', 'created_at']


class LabelSerializer(serializers.ModelSerializer):
    workspace_id = serializers.PrimaryKeyRelatedField(
        source='workspace', read_only=True,
    )

    class Meta:
        model = Label
        fields = [
            'id', 'workspace_id', 'name', 'color', 'description', 'created_at',
        ]
        read_only_fields = ['id', 'created_at']


class ProjectSerializer(serializers.ModelSerializer):
    workspace_id = serializers.PrimaryKeyRelatedField(
        source='workspace', read_only=True,
    )
    statuses = StatusSerializer(many=True, read_only=True)

    class Meta:
        model = Project
        fields = [
            'id', 'workspace_id', 'name', 'slug', 'description', 'icon',
            'color', 'sort_order', 'statuses', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ProjectCreateSerializer(serializers.ModelSerializer):
    workspace_id = serializers.PrimaryKeyRelatedField(
        source='workspace', read_only=True,
    )

    class Meta:
        model = Project
        fields = [
            'id', 'workspace_id', 'name', 'slug', 'description', 'icon',
            'color', 'sort_order',
        ]
        read_only_fields = ['id']


class IssueSerializer(serializers.ModelSerializer):
    workspace_id = serializers.PrimaryKeyRelatedField(
        source='workspace', read_only=True,
    )
    project_id = serializers.PrimaryKeyRelatedField(
        source='project', queryset=Project.objects.all(),
    )
    status_id = serializers.PrimaryKeyRelatedField(
        source='status', queryset=Status.objects.all(), required=False,
    )
    parent_id = serializers.PrimaryKeyRelatedField(
        source='parent', queryset=Issue.objects.all(),
        required=False, allow_null=True,
    )
    labels = LabelSerializer(many=True, read_only=True)
    label_ids = serializers.PrimaryKeyRelatedField(
        queryset=Label.objects.all(),
        many=True,
        write_only=True,
        required=False,
        source='labels',
    )
    sub_issue_count = serializers.SerializerMethodField()
    sub_issue_completed = serializers.SerializerMethodField()

    class Meta:
        model = Issue
        fields = [
            'id', 'identifier', 'number', 'workspace_id', 'project_id',
            'status_id', 'parent_id', 'title', 'description', 'priority',
            'estimate', 'labels', 'label_ids', 'sort_order',
            'created_at', 'updated_at', 'completed_at', 'cancelled_at',
            'sub_issue_count', 'sub_issue_completed',
        ]
        read_only_fields = [
            'id', 'identifier', 'number', 'created_at', 'updated_at',
            'completed_at', 'cancelled_at',
        ]

    def get_sub_issue_count(self, obj):
        return obj.sub_issues.count()

    def get_sub_issue_completed(self, obj):
        return obj.sub_issues.filter(status__category='completed').count()


class IssueCreateSerializer(serializers.Serializer):
    """Custom serializer for issue creation (uses services.create_issue)."""
    project_id = serializers.UUIDField()
    title = serializers.CharField(max_length=500)
    description = serializers.CharField(required=False, default='')
    priority = serializers.IntegerField(required=False, default=0)
    estimate = serializers.IntegerField(required=False, allow_null=True, default=None)
    status_id = serializers.UUIDField(required=False, allow_null=True)
    parent_id = serializers.UUIDField(required=False, allow_null=True)
    label_ids = serializers.ListField(
        child=serializers.UUIDField(), required=False, default=list
    )
    sort_order = serializers.FloatField(required=False, default=0)
