import SwiftUI

struct SidebarView: View {
    @EnvironmentObject var authService: AuthService

    var body: some View {
        List {
            Section("Workspace") {
                Text("Projects will appear here")
                    .foregroundColor(Theme.textSecondary)
            }
        }
        .listStyle(.sidebar)
        .toolbar {
            ToolbarItem(placement: .bottomBar) {
                Button("Sign Out") {
                    authService.logout()
                }
                .foregroundColor(Theme.accentRed)
            }
        }
        .navigationTitle("Minimalist")
    }
}
