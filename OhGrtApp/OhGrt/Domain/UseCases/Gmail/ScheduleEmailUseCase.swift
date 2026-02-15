import Foundation

protocol ScheduleEmailUseCaseProtocol: Sendable {
    func execute(
        to: String,
        subject: String,
        body: String,
        cc: String?,
        bcc: String?,
        scheduledAt: String,
        timezone: String
    ) async throws -> GmailSendResponseDTO
}

final class ScheduleEmailUseCase: ScheduleEmailUseCaseProtocol, @unchecked Sendable {
    private let repository: GmailRepositoryProtocol

    init(repository: GmailRepositoryProtocol) {
        self.repository = repository
    }

    func execute(
        to: String,
        subject: String,
        body: String,
        cc: String?,
        bcc: String?,
        scheduledAt: String,
        timezone: String
    ) async throws -> GmailSendResponseDTO {
        try await repository.scheduleEmail(
            to: to,
            subject: subject,
            body: body,
            cc: cc,
            bcc: bcc,
            scheduledAt: scheduledAt,
            timezone: timezone
        )
    }
}
