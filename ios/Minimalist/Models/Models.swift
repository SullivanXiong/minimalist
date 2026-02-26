import Foundation

struct Workspace: Codable, Identifiable {
    let id: String
    let name: String
    let slug: String
    let identifierPrefix: String
    let issueCounter: Int
    var description: String = ""
    var icon: String = ""

    enum CodingKeys: String, CodingKey {
        case id, name, slug, description, icon
        case identifierPrefix = "identifier_prefix"
        case issueCounter = "issue_counter"
    }
}

struct Project: Codable, Identifiable {
    let id: String
    let workspaceId: String
    let name: String
    let slug: String
    var description: String = ""
    var icon: String = ""
    var color: String = "#6B7280"
    var sortOrder: Double = 0
    var statuses: [Status] = []

    enum CodingKeys: String, CodingKey {
        case id, name, slug, description, icon, color, statuses
        case workspaceId = "workspace_id"
        case sortOrder = "sort_order"
    }
}

struct Status: Codable, Identifiable {
    let id: String
    let projectId: String
    let name: String
    let category: String
    var color: String = "#6B7280"
    var sortOrder: Double = 0
    var isDefault: Bool = false

    enum CodingKeys: String, CodingKey {
        case id, name, category, color
        case projectId = "project_id"
        case sortOrder = "sort_order"
        case isDefault = "is_default"
    }
}

struct Label: Codable, Identifiable {
    let id: String
    let workspaceId: String
    let name: String
    var color: String = "#6B7280"
    var description: String = ""

    enum CodingKeys: String, CodingKey {
        case id, name, color, description
        case workspaceId = "workspace_id"
    }
}

struct Issue: Codable, Identifiable {
    let id: String
    let identifier: String
    let number: Int
    let workspaceId: String
    let projectId: String
    let statusId: String
    var parentId: String?
    var assigneeId: Int?
    let title: String
    var description: String = ""
    var priority: Int = 0
    var estimate: Int?
    var labels: [Label] = []
    var sortOrder: Double = 0
    var subIssueCount: Int = 0
    var subIssueCompleted: Int = 0

    enum CodingKeys: String, CodingKey {
        case id, identifier, number, title, description, priority, estimate, labels
        case workspaceId = "workspace_id"
        case projectId = "project_id"
        case statusId = "status_id"
        case parentId = "parent_id"
        case assigneeId = "assignee_id"
        case sortOrder = "sort_order"
        case subIssueCount = "sub_issue_count"
        case subIssueCompleted = "sub_issue_completed"
    }
}

struct AuthTokens: Codable {
    let access: String
    let refresh: String
}

struct WorkspaceState: Codable {
    let workspace: Workspace
    let projects: [Project]
    let labels: [Label]
}

struct IssueCreateRequest: Codable {
    let projectId: String
    let title: String
    var description: String = ""
    var priority: Int = 0
    var statusId: String?
    var labelIds: [String] = []

    enum CodingKeys: String, CodingKey {
        case title, description, priority
        case projectId = "project_id"
        case statusId = "status_id"
        case labelIds = "label_ids"
    }
}
