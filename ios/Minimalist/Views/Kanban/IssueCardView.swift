import SwiftUI

struct IssueCardView: View {
    let issue: Issue

    var body: some View {
        VStack(alignment: .leading, spacing: 6) {
            // Priority + Identifier
            HStack {
                if issue.priority > 0 {
                    Text(Theme.priorityLabel(issue.priority))
                        .font(.caption2)
                        .foregroundColor(Theme.priorityColor(issue.priority))
                }
                Spacer()
                Text(issue.identifier)
                    .font(.caption2)
                    .foregroundColor(Theme.textMuted)
            }

            // Title
            Text(issue.title)
                .font(.subheadline)
                .foregroundColor(Theme.textPrimary)
                .lineLimit(3)

            // Labels
            if !issue.labels.isEmpty {
                HStack(spacing: 4) {
                    ForEach(issue.labels) { label in
                        Text(label.name)
                            .font(.caption2)
                            .padding(.horizontal, 6)
                            .padding(.vertical, 2)
                            .background(Color(hex: label.color).opacity(0.2))
                            .foregroundColor(Color(hex: label.color))
                            .cornerRadius(4)
                    }
                }
            }
        }
        .padding(10)
        .background(Theme.bgSurface)
        .cornerRadius(6)
    }
}
