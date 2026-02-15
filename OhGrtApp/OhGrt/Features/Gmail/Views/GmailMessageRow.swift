import SwiftUI

/// A row displaying a Gmail message summary in the inbox list
struct GmailMessageRow: View {
    let message: GmailMessageSummary
    let index: Int

    @ObservedObject private var theme = ThemeManager.shared
    @State private var appeared = false

    var body: some View {
        HStack(spacing: 14) {
            // Sender avatar
            ZStack {
                Circle()
                    .fill(theme.primaryGradient)
                    .frame(width: 44, height: 44)

                Text(senderInitial)
                    .font(.system(size: 18, weight: .semibold))
                    .foregroundColor(.white)
            }

            VStack(alignment: .leading, spacing: 4) {
                HStack {
                    Text(senderName)
                        .font(.subheadline)
                        .fontWeight(.semibold)
                        .foregroundColor(.primary)
                        .lineLimit(1)

                    Spacer()

                    Text(smartDate)
                        .font(.caption2)
                        .foregroundColor(.secondary)
                }

                Text(message.subject)
                    .font(.subheadline)
                    .fontWeight(.medium)
                    .foregroundColor(.primary)
                    .lineLimit(1)

                Text(message.snippet)
                    .font(.caption)
                    .foregroundColor(.secondary)
                    .lineLimit(2)
            }

            Image(systemName: "chevron.right")
                .font(.system(size: 12, weight: .semibold))
                .foregroundColor(.secondary)
        }
        .padding(14)
        .background(
            RoundedRectangle(cornerRadius: 16)
                .fill(Color(.secondarySystemBackground))
        )
        .opacity(appeared ? 1 : 0)
        .offset(y: appeared ? 0 : 12)
        .onAppear {
            withAnimation(.spring(response: 0.4, dampingFraction: 0.7).delay(Double(index) * 0.05)) {
                appeared = true
            }
        }
    }

    // MARK: - Computed

    private var senderName: String {
        let from = message.from
        // Parse "Name <email>" format
        if let angleBracket = from.firstIndex(of: "<") {
            return String(from[from.startIndex..<angleBracket]).trimmingCharacters(in: .whitespaces)
        }
        // Parse "email@domain.com" - use part before @
        if from.contains("@") {
            return String(from.split(separator: "@").first ?? Substring(from))
        }
        return from
    }

    private var senderInitial: String {
        String(senderName.prefix(1)).uppercased()
    }

    private var smartDate: String {
        // Parse the date string and format smartly
        let dateStr = message.date
        let formatter = DateFormatter()

        // Try common date formats
        let formats = [
            "EEE, dd MMM yyyy HH:mm:ss Z",
            "yyyy-MM-dd'T'HH:mm:ssZ",
            "yyyy-MM-dd'T'HH:mm:ss.SSSZ",
            "dd MMM yyyy HH:mm:ss Z"
        ]

        var parsed: Date?
        for format in formats {
            formatter.dateFormat = format
            formatter.locale = Locale(identifier: "en_US_POSIX")
            if let date = formatter.date(from: dateStr) {
                parsed = date
                break
            }
        }

        guard let date = parsed else {
            // Fallback: return first few chars
            return String(dateStr.prefix(10))
        }

        let calendar = Calendar.current
        let now = Date()

        if calendar.isDateInToday(date) {
            let timeFormatter = DateFormatter()
            timeFormatter.dateFormat = "h:mm a"
            return timeFormatter.string(from: date)
        } else if calendar.isDateInYesterday(date) {
            return "Yesterday"
        } else if let daysAgo = calendar.dateComponents([.day], from: date, to: now).day, daysAgo < 7 {
            let dayFormatter = DateFormatter()
            dayFormatter.dateFormat = "EEEE"
            return dayFormatter.string(from: date)
        } else {
            let dateFormatter = DateFormatter()
            dateFormatter.dateFormat = "MMM d"
            return dateFormatter.string(from: date)
        }
    }
}
