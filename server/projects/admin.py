from django.contrib import admin

from .models import Issue, Label, Project, Status, Workspace


class StatusInline(admin.TabularInline):
    model = Status
    extra = 0
    fields = ('name', 'category', 'color', 'sort_order', 'is_default')


@admin.register(Workspace)
class WorkspaceAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'identifier_prefix', 'issue_counter', 'created_at')
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'workspace', 'color', 'sort_order', 'created_at')
    list_filter = ('workspace',)
    search_fields = ('name',)
    inlines = [StatusInline]


@admin.register(Status)
class StatusAdmin(admin.ModelAdmin):
    list_display = ('name', 'project', 'category', 'color', 'sort_order', 'is_default')
    list_filter = ('category', 'project')
    search_fields = ('name',)


@admin.register(Label)
class LabelAdmin(admin.ModelAdmin):
    list_display = ('name', 'workspace', 'color', 'created_at')
    list_filter = ('workspace',)
    search_fields = ('name',)


@admin.register(Issue)
class IssueAdmin(admin.ModelAdmin):
    list_display = ('identifier', 'title', 'project', 'status', 'priority', 'created_at')
    list_filter = ('project', 'status', 'priority', 'workspace')
    search_fields = ('identifier', 'title', 'description')
    filter_horizontal = ('labels',)
    raw_id_fields = ('parent', 'assignee')
