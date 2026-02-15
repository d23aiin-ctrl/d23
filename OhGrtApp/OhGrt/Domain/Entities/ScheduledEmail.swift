import Foundation

/// Status of a scheduled email
enum ScheduledEmailStatus: String, CaseIterable, Sendable {
    case active
    case completed
    case cancelled
    case failed

    var displayName: String {
        switch self {
        case .active: return "Scheduled"
        case .completed: return "Sent"
        case .cancelled: return "Cancelled"
        case .failed: return "Failed"
        }
    }
}

/// Domain entity for a scheduled email
struct ScheduledEmail: Identifiable, Equatable, Sendable {
    let id: String
    let to: String
    let subject: String
    let body: String
    let cc: String?
    let bcc: String?
    let scheduledAt: String
    let status: ScheduledEmailStatus
    let createdAt: String?
    let lastRunAt: String?
    let runCount: Int
}
