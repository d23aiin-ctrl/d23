import Foundation

/// Implementation of GmailRepositoryProtocol
final class GmailRepository: GmailRepositoryProtocol, @unchecked Sendable {
    private let apiClient: APIClient

    init(apiClient: APIClient) {
        self.apiClient = apiClient
    }

    func search(query: String) async throws -> [GmailMessageSummary] {
        try await apiClient.searchGmail(query: query)
    }

    func getMessage(id: String) async throws -> GmailMessageDetail {
        try await apiClient.getGmailMessage(id: id)
    }

    func sendMessage(
        to: String,
        subject: String,
        body: String,
        cc: String?,
        bcc: String?,
        html: Bool
    ) async throws -> GmailSendResponseDTO {
        try await apiClient.sendGmailMessage(
            to: to,
            subject: subject,
            body: body,
            cc: cc,
            bcc: bcc,
            html: html
        )
    }

    func scheduleEmail(
        to: String,
        subject: String,
        body: String,
        cc: String?,
        bcc: String?,
        scheduledAt: String,
        timezone: String
    ) async throws -> GmailSendResponseDTO {
        let request = ScheduleEmailRequestDTO(
            to: to,
            subject: subject,
            body: body,
            cc: cc,
            bcc: bcc,
            scheduledAt: scheduledAt,
            timezone: timezone
        )
        return try await apiClient.scheduleEmail(request: request)
    }

    func getScheduledEmails(status: String?) async throws -> [ScheduledEmail] {
        let dtos = try await apiClient.getScheduledEmails(status: status)
        return dtos.map { ScheduledEmailMapper.toDomain($0) }
    }

    func updateScheduledEmail(
        id: String,
        to: String?,
        subject: String?,
        body: String?,
        scheduledAt: String?
    ) async throws -> ScheduledEmail {
        let request = UpdateScheduledEmailRequestDTO(
            to: to,
            subject: subject,
            body: body,
            scheduledAt: scheduledAt
        )
        let dto = try await apiClient.updateScheduledEmail(id: id, request: request)
        return ScheduledEmailMapper.toDomain(dto)
    }

    func deleteScheduledEmail(id: String) async throws {
        try await apiClient.deleteScheduledEmail(id: id)
    }
}
