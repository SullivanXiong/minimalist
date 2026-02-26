import SwiftUI

struct KanbanBoardView: View {
    var body: some View {
        ScrollView(.horizontal) {
            HStack(alignment: .top, spacing: 12) {
                Text("Kanban board will be connected to workspace data")
                    .foregroundColor(Theme.textSecondary)
                    .padding()
            }
            .padding()
        }
        .background(Theme.bgPrimary)
        .navigationTitle("Board")
    }
}
