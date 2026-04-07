import SwiftUI

struct KanbanColumnView: View {
    let status: Status
    let issues: [Issue]

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            // Column header
            HStack {
                Circle()
                    .fill(Theme.statusColor(status.category))
                    .frame(width: 8, height: 8)
                Text(status.name)
                    .font(.subheadline)
                    .fontWeight(.medium)
                    .foregroundColor(Theme.textSecondary)
                Text("\(issues.count)")
                    .font(.caption)
                    .foregroundColor(Theme.textMuted)
            }
            .padding(.horizontal, 12)
            .padding(.top, 12)

            // Issue cards
            ScrollView {
                LazyVStack(spacing: 4) {
                    ForEach(issues) { issue in
                        IssueCardView(issue: issue)
                    }
                }
                .padding(.horizontal, 8)
            }
        }
        .frame(width: 280)
        .background(Theme.bgSecondary)
        .cornerRadius(8)
    }
}
