import Foundation

enum AppEnvironment: String {
    case development
    case staging
    case production
}

struct Configuration {
    static let shared = Configuration()

    let environment: AppEnvironment
    let baseURL: URL
    let wsURL: URL

    private init() {
        #if DEBUG
        self.environment = .development
        self.baseURL = URL(string: "http://localhost:8000")!
        self.wsURL = URL(string: "ws://localhost:8000")!
        #else
        self.environment = .production
        self.baseURL = URL(string: "https://minimalist.example.com")!
        self.wsURL = URL(string: "wss://minimalist.example.com")!
        #endif
    }
}
