import Foundation

/// Repository for Gmail operations
protocol GmailRepositoryProtocol: Sendable {
    func search(query: String) async throws -> [GmailMessageSummary]
    func getMessage(id: String) async throws -> GmailMessageDetail
    func sendMessage(
        to: String,
        subject: String,
        body: String,
        cc: String?,
        bcc: String?,
        html: Bool
    ) async throws -> GmailSendResponseDTO

    func scheduleEmail(
        to: String,
        subject: String,
        body: String,
        cc: String?,
        bcc: String?,
        scheduledAt: String,
        timezone: String
    ) async throws -> GmailSendResponseDTO

    func getScheduledEmails(status: String?) async throws -> [ScheduledEmail]

    func updateScheduledEmail(
        id: String,
        to: String?,
        subject: String?,
        body: String?,
        scheduledAt: String?
    ) async throws -> ScheduledEmail

    func deleteScheduledEmail(id: String) async throws
}
