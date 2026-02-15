import Foundation

protocol GetScheduledEmailsUseCaseProtocol: Sendable {
    func execute(status: String?) async throws -> [ScheduledEmail]
}

final class GetScheduledEmailsUseCase: GetScheduledEmailsUseCaseProtocol, @unchecked Sendable {
    private let repository: GmailRepositoryProtocol

    init(repository: GmailRepositoryProtocol) {
        self.repository = repository
    }

    func execute(status: String?) async throws -> [ScheduledEmail] {
        try await repository.getScheduledEmails(status: status)
    }
}
