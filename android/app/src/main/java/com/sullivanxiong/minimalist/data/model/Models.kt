package com.sullivanxiong.minimalist.data.model

import com.squareup.moshi.JsonClass

@JsonClass(generateAdapter = true)
data class Workspace(
    val id: String,
    val name: String,
    val slug: String,
    val identifier_prefix: String,
    val issue_counter: Int,
    val description: String = "",
    val icon: String = "",
)

@JsonClass(generateAdapter = true)
data class Project(
    val id: String,
    val workspace_id: String,
    val name: String,
    val slug: String,
    val description: String = "",
    val icon: String = "",
    val color: String = "#6B7280",
    val sort_order: Double = 0.0,
    val statuses: List<Status> = emptyList(),
)

@JsonClass(generateAdapter = true)
data class Status(
    val id: String,
    val project_id: String,
    val name: String,
    val category: String,
    val color: String = "#6B7280",
    val sort_order: Double = 0.0,
    val is_default: Boolean = false,
)

@JsonClass(generateAdapter = true)
data class Label(
    val id: String,
    val workspace_id: String,
    val name: String,
    val color: String = "#6B7280",
    val description: String = "",
)

@JsonClass(generateAdapter = true)
data class Issue(
    val id: String,
    val identifier: String,
    val number: Int,
    val workspace_id: String,
    val project_id: String,
    val status_id: String,
    val parent_id: String? = null,
    val assignee_id: Int? = null,
    val title: String,
    val description: String = "",
    val priority: Int = 0,
    val estimate: Int? = null,
    val labels: List<Label> = emptyList(),
    val sort_order: Double = 0.0,
    val sub_issue_count: Int = 0,
    val sub_issue_completed: Int = 0,
)

@JsonClass(generateAdapter = true)
data class AuthTokens(
    val access: String,
    val refresh: String,
)

@JsonClass(generateAdapter = true)
data class WorkspaceState(
    val workspace: Workspace,
    val projects: List<Project>,
    val labels: List<Label>,
)

@JsonClass(generateAdapter = true)
data class LoginRequest(
    val username: String,
    val password: String,
)

@JsonClass(generateAdapter = true)
data class RefreshRequest(
    val refresh: String,
)

@JsonClass(generateAdapter = true)
data class IssueCreateRequest(
    val project_id: String,
    val title: String,
    val description: String = "",
    val priority: Int = 0,
    val status_id: String? = null,
    val label_ids: List<String> = emptyList(),
)
