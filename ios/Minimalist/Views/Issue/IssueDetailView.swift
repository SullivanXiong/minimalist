import SwiftUI

struct IssueDetailView: View {
    let issue: Issue

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 16) {
                // Header
                HStack {
                    Text(issue.identifier)
                        .font(.caption)
                        .foregroundColor(Theme.textMuted)
                    Spacer()
                    if issue.priority > 0 {
                        Text(Theme.priorityLabel(issue.priority))
                            .font(.caption)
                            .foregroundColor(Theme.priorityColor(issue.priority))
                    }
                }

                Text(issue.title)
                    .font(.title2)
                    .fontWeight(.semibold)
                    .foregroundColor(Theme.textPrimary)

                if !issue.description.isEmpty {
                    Text(issue.description)
                        .font(.body)
                        .foregroundColor(Theme.textSecondary)
                }

                Divider().background(Theme.borderPrimary)

                // Properties
                VStack(alignment: .leading, spacing: 12) {
                    if let estimate = issue.estimate {
                        PropertyRow(label: "Estimate", value: "\(estimate) points")
                    }

                    if issue.subIssueCount > 0 {
                        PropertyRow(
                            label: "Sub-issues",
                            value: "\(issue.subIssueCompleted)/\(issue.subIssueCount)"
                        )
                    }

                    if !issue.labels.isEmpty {
                        Text("Labels")
                            .font(.caption)
                            .foregroundColor(Theme.textMuted)
                        FlowLayout(spacing: 4) {
                            ForEach(issue.labels) { label in
                                Text(label.name)
                                    .font(.caption)
                                    .padding(.horizontal, 8)
                                    .padding(.vertical, 3)
                                    .background(Color(hex: label.color).opacity(0.2))
                                    .foregroundColor(Color(hex: label.color))
                                    .cornerRadius(4)
                            }
                        }
                    }
                }
            }
            .padding()
        }
        .background(Theme.bgPrimary)
        .navigationTitle(issue.identifier)
        .navigationBarTitleDisplayMode(.inline)
    }
}

struct PropertyRow: View {
    let label: String
    let value: String

    var body: some View {
        HStack {
            Text(label)
                .font(.caption)
                .foregroundColor(Theme.textMuted)
                .frame(width: 80, alignment: .leading)
            Text(value)
                .font(.subheadline)
                .foregroundColor(Theme.textPrimary)
        }
    }
}

/// Simple flow layout for labels
struct FlowLayout: Layout {
    var spacing: CGFloat = 4

    func sizeThatFits(proposal: ProposedViewSize, subviews: Subviews, cache: inout ()) -> CGSize {
        let width = proposal.width ?? .infinity
        var x: CGFloat = 0
        var y: CGFloat = 0
        var maxHeight: CGFloat = 0

        for subview in subviews {
            let size = subview.sizeThatFits(.unspecified)
            if x + size.width > width, x > 0 {
                x = 0
                y += maxHeight + spacing
                maxHeight = 0
            }
            x += size.width + spacing
            maxHeight = max(maxHeight, size.height)
        }

        return CGSize(width: width, height: y + maxHeight)
    }

    func placeSubviews(in bounds: CGRect, proposal: ProposedViewSize, subviews: Subviews, cache: inout ()) {
        var x = bounds.minX
        var y = bounds.minY
        var maxHeight: CGFloat = 0

        for subview in subviews {
            let size = subview.sizeThatFits(.unspecified)
            if x + size.width > bounds.maxX, x > bounds.minX {
                x = bounds.minX
                y += maxHeight + spacing
                maxHeight = 0
            }
            subview.place(at: CGPoint(x: x, y: y), proposal: .unspecified)
            x += size.width + spacing
            maxHeight = max(maxHeight, size.height)
        }
    }
}
