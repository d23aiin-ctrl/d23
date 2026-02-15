import Foundation

protocol UpdateScheduledEmailUseCaseProtocol: Sendable {
    func execute(
        id: String,
        to: String?,
        subject: String?,
        body: String?,
        scheduledAt: String?
    ) async throws -> ScheduledEmail
}

final class UpdateScheduledEmailUseCase: UpdateScheduledEmailUseCaseProtocol, @unchecked Sendable {
    private let repository: GmailRepositoryProtocol

    init(repository: GmailRepositoryProtocol) {
        self.repository = repository
    }

    func execute(
        id: String,
        to: String?,
        subject: String?,
        body: String?,
        scheduledAt: String?
    ) async throws -> ScheduledEmail {
        try await repository.updateScheduledEmail(
            id: id,
            to: to,
            subject: subject,
            body: body,
            scheduledAt: scheduledAt
        )
    }
}
