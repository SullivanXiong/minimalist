import SwiftUI

struct IssueListView: View {
    let issues: [Issue]
    var onSelect: ((Issue) -> Void)?

    var body: some View {
        List(issues) { issue in
            Button {
                onSelect?(issue)
            } label: {
                HStack(spacing: 12) {
                    // Priority indicator
                    Circle()
                        .fill(Theme.priorityColor(issue.priority))
                        .frame(width: 6, height: 6)

                    // Identifier
                    Text(issue.identifier)
                        .font(.caption)
                        .foregroundColor(Theme.textMuted)
                        .frame(width: 60, alignment: .leading)

                    // Title
                    Text(issue.title)
                        .font(.subheadline)
                        .foregroundColor(Theme.textPrimary)
                        .lineLimit(1)

                    Spacer()

                    // Labels
                    ForEach(issue.labels.prefix(2)) { label in
                        Text(label.name)
                            .font(.caption2)
                            .padding(.horizontal, 4)
                            .padding(.vertical, 1)
                            .background(Color(hex: label.color).opacity(0.2))
                            .foregroundColor(Color(hex: label.color))
                            .cornerRadius(3)
                    }
                }
            }
            .listRowBackground(Theme.bgPrimary)
        }
        .listStyle(.plain)
        .background(Theme.bgPrimary)
    }
}
