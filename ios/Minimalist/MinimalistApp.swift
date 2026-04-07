import SwiftUI

@main
struct MinimalistApp: App {
    @StateObject private var authService = AuthService()

    var body: some Scene {
        WindowGroup {
            ContentView()
                .environmentObject(authService)
                .preferredColorScheme(.dark)
        }
    }
}
