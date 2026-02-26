import SwiftUI

/// Dark theme matching the desktop client's color palette.
enum Theme {
    // Backgrounds
    static let bgPrimary = Color(hex: "0D0D0D")
    static let bgSecondary = Color(hex: "141414")
    static let bgSurface = Color(hex: "1A1A1A")
    static let bgHover = Color(hex: "222222")
    static let bgSelected = Color(hex: "2A2A2A")

    // Text
    static let textPrimary = Color(hex: "EBEBEB")
    static let textSecondary = Color(hex: "8A8A8A")
    static let textMuted = Color(hex: "5C5C5C")

    // Accents
    static let accentPurple = Color(hex: "7C5CFC")
    static let accentBlue = Color(hex: "5E6AD2")
    static let accentGreen = Color(hex: "10B981")
    static let accentYellow = Color(hex: "F59E0B")
    static let accentRed = Color(hex: "EF4444")
    static let accentOrange = Color(hex: "F97316")

    // Borders
    static let borderPrimary = Color(hex: "2A2A2A")

    // Status category colors
    static func statusColor(_ category: String) -> Color {
        switch category {
        case "backlog", "unstarted": return Color(hex: "6B7280")
        case "started": return accentYellow
        case "completed": return accentGreen
        case "cancelled": return accentRed
        default: return Color(hex: "6B7280")
        }
    }

    // Priority colors
    static func priorityColor(_ priority: Int) -> Color {
        switch priority {
        case 1: return accentRed
        case 2: return accentOrange
        case 3: return accentYellow
        case 4: return Color(hex: "6B7280")
        default: return Color(hex: "6B7280")
        }
    }

    static func priorityLabel(_ priority: Int) -> String {
        switch priority {
        case 1: return "Urgent"
        case 2: return "High"
        case 3: return "Medium"
        case 4: return "Low"
        default: return "No Priority"
        }
    }
}

extension Color {
    init(hex: String) {
        let hex = hex.trimmingCharacters(in: CharacterSet.alphanumerics.inverted)
        var int: UInt64 = 0
        Scanner(string: hex).scanHexInt64(&int)
        let r, g, b: UInt64
        (r, g, b) = ((int >> 16) & 0xFF, (int >> 8) & 0xFF, int & 0xFF)
        self.init(
            .sRGB,
            red: Double(r) / 255,
            green: Double(g) / 255,
            blue: Double(b) / 255,
            opacity: 1
        )
    }
}
