import SwiftUI

/// Card displaying a single scheduled email
struct ScheduledEmailCard: View {
    let email: ScheduledEmail
    let onEdit: () -> Void
    let onCancel: () -> Void

    @ObservedObject private var theme = ThemeManager.shared

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            // Top row: status badge + time
            HStack {
                statusBadge
                Spacer()
                if email.status == .active {
                    Text(timeRemaining)
                        .font(.caption2)
                        .fontWeight(.medium)
                        .foregroundColor(.orange)
                }
            }

            // Recipient
            HStack(spacing: 6) {
                Image(systemName: "person.fill")
                    .font(.system(size: 12))
                    .foregroundColor(.secondary)
                Text(email.to)
                    .font(.caption)
                    .foregroundColor(.primary)
                    .lineLimit(1)
            }

            // Subject
            Text(email.subject)
                .font(.subheadline)
                .fontWeight(.semibold)
                .foregroundColor(.primary)
                .lineLimit(2)

            Divider()

            // Scheduled time
            HStack {
                Image(systemName: "clock.fill")
                    .font(.system(size: 12))
                    .foregroundColor(.secondary)

                Text(formattedScheduledTime)
                    .font(.caption)
                    .foregroundColor(.secondary)

                Spacer()

                if email.status == .active {
                    Menu {
                        Button {
                            onEdit()
                        } label: {
                            Label("Edit", systemImage: "pencil")
                        }

                        Button(role: .destructive) {
                            onCancel()
                        } label: {
                            Label("Cancel", systemImage: "xmark.circle")
                        }
                    } label: {
                        Image(systemName: "ellipsis.circle")
                            .font(.system(size: 18))
                            .foregroundColor(.secondary)
                    }
                }
            }
        }
        .padding(16)
        .background(
            RoundedRectangle(cornerRadius: 16)
                .fill(Color(.secondarySystemBackground))
        )
    }

    // MARK: - Status Badge

    private var statusBadge: some View {
        HStack(spacing: 4) {
            Circle()
                .fill(statusColor)
                .frame(width: 8, height: 8)

            Text(email.status.displayName)
                .font(.caption2)
                .fontWeight(.bold)
        }
        .foregroundColor(statusColor)
        .padding(.horizontal, 10)
        .padding(.vertical, 4)
        .background(
            Capsule()
                .fill(statusColor.opacity(0.12))
        )
    }

    private var statusColor: Color {
        switch email.status {
        case .active: return .blue
        case .completed: return .green
        case .cancelled: return .red
        case .failed: return .orange
        }
    }

    // MARK: - Date Helpers

    private var formattedScheduledTime: String {
        guard let date = parseDate(email.scheduledAt) else {
            return email.scheduledAt
        }
        let formatter = DateFormatter()
        formatter.dateStyle = .medium
        formatter.timeStyle = .short
        return formatter.string(from: date)
    }

    private var timeRemaining: String {
        guard let date = parseDate(email.scheduledAt) else { return "" }
        let interval = date.timeIntervalSince(Date())
        guard interval > 0 else { return "Due" }

        let hours = Int(interval) / 3600
        let minutes = (Int(interval) % 3600) / 60

        if hours > 24 {
            let days = hours / 24
            return "in \(days)d"
        } else if hours > 0 {
            return "in \(hours)h \(minutes)m"
        } else {
            return "in \(minutes)m"
        }
    }

    private func parseDate(_ dateStr: String) -> Date? {
        let formatter = ISO8601DateFormatter()
        formatter.formatOptions = [.withInternetDateTime, .withFractionalSeconds]
        if let date = formatter.date(from: dateStr) { return date }
        formatter.formatOptions = [.withInternetDateTime]
        return formatter.date(from: dateStr)
    }
}
