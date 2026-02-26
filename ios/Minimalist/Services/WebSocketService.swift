import Foundation

/// WebSocket client for real-time workspace updates.
@MainActor
class WebSocketService: ObservableObject {
    @Published var isConnected = false

    private var webSocket: URLSessionWebSocketTask?
    private var onMessage: ((String, [String: Any]) -> Void)?

    func connect(workspaceSlug: String, token: String?) {
        disconnect()

        let wsURL = Configuration.shared.wsURL
        var urlString = "\(wsURL)/ws/workspace/\(workspaceSlug)/"
        if let token {
            urlString += "?token=\(token)"
        }

        guard let url = URL(string: urlString) else { return }

        let session = URLSession(configuration: .default)
        webSocket = session.webSocketTask(with: url)
        webSocket?.resume()
        isConnected = true
        receiveMessage()
    }

    func disconnect() {
        webSocket?.cancel(with: .normalClosure, reason: nil)
        webSocket = nil
        isConnected = false
    }

    func send(type: String, data: [String: Any]) {
        let message: [String: Any] = ["type": type, "data": data]
        guard let jsonData = try? JSONSerialization.data(withJSONObject: message),
              let jsonString = String(data: jsonData, encoding: .utf8) else { return }
        webSocket?.send(.string(jsonString)) { _ in }
    }

    func onMessage(_ handler: @escaping (String, [String: Any]) -> Void) {
        self.onMessage = handler
    }

    private func receiveMessage() {
        webSocket?.receive { [weak self] result in
            switch result {
            case .success(let message):
                switch message {
                case .string(let text):
                    if let data = text.data(using: .utf8),
                       let json = try? JSONSerialization.jsonObject(with: data) as? [String: Any] {
                        let type = json["type"] as? String ?? ""
                        let msgData = json["data"] as? [String: Any] ?? [:]
                        Task { @MainActor [weak self] in
                            self?.onMessage?(type, msgData)
                        }
                    }
                default:
                    break
                }
                Task { @MainActor [weak self] in
                    self?.receiveMessage()
                }
            case .failure:
                Task { @MainActor [weak self] in
                    self?.isConnected = false
                }
            }
        }
    }
}
