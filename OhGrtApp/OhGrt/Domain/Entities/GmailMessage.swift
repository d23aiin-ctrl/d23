import Foundation

/// Gmail message summary for list views
struct GmailMessageSummary: Identifiable, Equatable, Hashable, Sendable {
    let id: String
    let snippet: String
    let subject: String
    let from: String
    let date: String
}

/// Full Gmail message detail
struct GmailMessageDetail: Identifiable, Equatable, Sendable {
    let id: String
    let threadId: String?
    let snippet: String
    let subject: String
    let from: String
    let to: String
    let cc: String?
    let date: String
    let body: String
    let labelIds: [String]
}
