import Foundation
import SwiftUI

@MainActor
class AuthService: ObservableObject {
    @Published var isAuthenticated = false
    @Published var error: String?

    private static let accessTokenKey = "minimalist_access_token"
    private static let refreshTokenKey = "minimalist_refresh_token"

    init() {
        isAuthenticated = Self.getStoredAccessToken() != nil
    }

    func login(username: String, password: String) async {
        do {
            let tokens = try await APIClient.shared.login(
                username: username, password: password
            )
            Self.storeTokens(tokens)
            isAuthenticated = true
            error = nil
        } catch {
            self.error = error.localizedDescription
        }
    }

    func logout() {
        Self.clearTokens()
        isAuthenticated = false
    }

    // MARK: - Keychain Storage

    static func getStoredAccessToken() -> String? {
        KeychainHelper.read(key: accessTokenKey)
    }

    static func getStoredRefreshToken() -> String? {
        KeychainHelper.read(key: refreshTokenKey)
    }

    static func storeTokens(_ tokens: AuthTokens) {
        KeychainHelper.save(key: accessTokenKey, value: tokens.access)
        KeychainHelper.save(key: refreshTokenKey, value: tokens.refresh)
    }

    static func clearTokens() {
        KeychainHelper.delete(key: accessTokenKey)
        KeychainHelper.delete(key: refreshTokenKey)
    }
}

// Simple Keychain wrapper
enum KeychainHelper {
    static func save(key: String, value: String) {
        let data = value.data(using: .utf8)!
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrAccount as String: key,
            kSecValueData as String: data,
        ]
        SecItemDelete(query as CFDictionary)
        SecItemAdd(query as CFDictionary, nil)
    }

    static func read(key: String) -> String? {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrAccount as String: key,
            kSecReturnData as String: true,
            kSecMatchLimit as String: kSecMatchLimitOne,
        ]
        var result: AnyObject?
        let status = SecItemCopyMatching(query as CFDictionary, &result)
        guard status == errSecSuccess, let data = result as? Data else { return nil }
        return String(data: data, encoding: .utf8)
    }

    static func delete(key: String) {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrAccount as String: key,
        ]
        SecItemDelete(query as CFDictionary)
    }
}
