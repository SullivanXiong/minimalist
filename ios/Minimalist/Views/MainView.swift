import SwiftUI

struct MainView: View {
    @EnvironmentObject var authService: AuthService

    var body: some View {
        NavigationSplitView {
            SidebarView()
        } detail: {
            KanbanBoardView()
        }
        .background(Theme.bgPrimary)
    }
}
