import Foundation

protocol DeleteScheduledEmailUseCaseProtocol: Sendable {
    func execute(id: String) async throws
}

final class DeleteScheduledEmailUseCase: DeleteScheduledEmailUseCaseProtocol, @unchecked Sendable {
    private let repository: GmailRepositoryProtocol

    init(repository: GmailRepositoryProtocol) {
        self.repository = repository
    }

    func execute(id: String) async throws {
        try await repository.deleteScheduledEmail(id: id)
    }
}
