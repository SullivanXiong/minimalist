import Foundation

/// Local cache for offline support using UserDefaults (SwiftData in v2).
class LocalStore {
    static let shared = LocalStore()

    private let defaults = UserDefaults.standard
    private let encoder = JSONEncoder()
    private let decoder = JSONDecoder()

    // MARK: - Workspace State Cache

    func cacheWorkspaceState(_ state: WorkspaceState, slug: String) {
        if let data = try? encoder.encode(state) {
            defaults.set(data, forKey: "workspace_\(slug)")
        }
    }

    func getCachedWorkspaceState(slug: String) -> WorkspaceState? {
        guard let data = defaults.data(forKey: "workspace_\(slug)") else { return nil }
        return try? decoder.decode(WorkspaceState.self, from: data)
    }

    // MARK: - Issues Cache

    func cacheIssues(_ issues: [Issue], projectId: String) {
        if let data = try? encoder.encode(issues) {
            defaults.set(data, forKey: "issues_\(projectId)")
        }
    }

    func getCachedIssues(projectId: String) -> [Issue]? {
        guard let data = defaults.data(forKey: "issues_\(projectId)") else { return nil }
        return try? decoder.decode([Issue].self, from: data)
    }

    // MARK: - Preferences

    var lastWorkspaceSlug: String? {
        get { defaults.string(forKey: "last_workspace_slug") }
        set { defaults.set(newValue, forKey: "last_workspace_slug") }
    }

    var lastProjectId: String? {
        get { defaults.string(forKey: "last_project_id") }
        set { defaults.set(newValue, forKey: "last_project_id") }
    }
}
