import Foundation

enum APIError: Error, LocalizedError {
    case invalidResponse
    case unauthorized
    case serverError(Int)
    case decodingError(Error)
    case networkError(Error)

    var errorDescription: String? {
        switch self {
        case .invalidResponse: return "Invalid server response"
        case .unauthorized: return "Authentication required"
        case .serverError(let code): return "Server error (\(code))"
        case .decodingError(let err): return "Data error: \(err.localizedDescription)"
        case .networkError(let err): return "Network error: \(err.localizedDescription)"
        }
    }
}

actor APIClient {
    static let shared = APIClient()

    private let baseURL: URL
    private let session: URLSession
    private let decoder: JSONDecoder

    private init() {
        self.baseURL = Configuration.shared.baseURL
        self.session = URLSession.shared
        self.decoder = JSONDecoder()
    }

    // MARK: - Auth

    func login(username: String, password: String) async throws -> AuthTokens {
        let body = ["username": username, "password": password]
        return try await post("api/auth/login/", body: body)
    }

    func refreshToken(_ refreshToken: String) async throws -> AuthTokens {
        let body = ["refresh": refreshToken]
        return try await post("api/auth/refresh/", body: body)
    }

    // MARK: - Workspaces

    func getWorkspaces() async throws -> [Workspace] {
        return try await get("api/v1/workspaces/")
    }

    // MARK: - Projects

    func getProjects(workspaceSlug: String) async throws -> [Project] {
        return try await get("api/v1/workspaces/\(workspaceSlug)/projects/")
    }

    // MARK: - Issues

    func getIssues(workspaceSlug: String, projectId: String? = nil) async throws -> [Issue] {
        var path = "api/v1/workspaces/\(workspaceSlug)/issues/"
        if let projectId {
            path += "?project_id=\(projectId)"
        }
        return try await get(path)
    }

    func createIssue(workspaceSlug: String, request: IssueCreateRequest) async throws -> Issue {
        return try await post("api/v1/workspaces/\(workspaceSlug)/issues/", body: request)
    }

    func moveIssue(workspaceSlug: String, issueId: String, statusId: String) async throws -> Issue {
        let body = ["status_id": statusId]
        return try await post("api/v1/workspaces/\(workspaceSlug)/issues/\(issueId)/move/", body: body)
    }

    // MARK: - Labels

    func getLabels(workspaceSlug: String) async throws -> [Label] {
        return try await get("api/v1/workspaces/\(workspaceSlug)/labels/")
    }

    // MARK: - HTTP Helpers

    private func get<T: Decodable>(_ path: String) async throws -> T {
        let url = baseURL.appendingPathComponent(path)
        var request = URLRequest(url: url)
        request.httpMethod = "GET"
        addAuth(&request)
        return try await execute(request)
    }

    private func post<T: Decodable, B: Encodable>(_ path: String, body: B) async throws -> T {
        let url = baseURL.appendingPathComponent(path)
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.httpBody = try JSONEncoder().encode(body)
        addAuth(&request)
        return try await execute(request)
    }

    private func addAuth(_ request: inout URLRequest) {
        if let token = AuthService.getStoredAccessToken() {
            request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        }
    }

    private func execute<T: Decodable>(_ request: URLRequest) async throws -> T {
        let (data, response): (Data, URLResponse)
        do {
            (data, response) = try await session.data(for: request)
        } catch {
            throw APIError.networkError(error)
        }

        guard let httpResponse = response as? HTTPURLResponse else {
            throw APIError.invalidResponse
        }

        guard (200...299).contains(httpResponse.statusCode) else {
            if httpResponse.statusCode == 401 {
                throw APIError.unauthorized
            }
            throw APIError.serverError(httpResponse.statusCode)
        }

        do {
            return try decoder.decode(T.self, from: data)
        } catch {
            throw APIError.decodingError(error)
        }
    }
}
