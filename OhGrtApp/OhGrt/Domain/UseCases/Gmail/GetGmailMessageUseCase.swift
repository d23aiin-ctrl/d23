import Foundation

protocol GetGmailMessageUseCaseProtocol: Sendable {
    func execute(id: String) async throws -> GmailMessageDetail
}

final class GetGmailMessageUseCase: GetGmailMessageUseCaseProtocol, @unchecked Sendable {
    private let repository: GmailRepositoryProtocol

    init(repository: GmailRepositoryProtocol) {
        self.repository = repository
    }

    func execute(id: String) async throws -> GmailMessageDetail {
        try await repository.getMessage(id: id)
    }
}
