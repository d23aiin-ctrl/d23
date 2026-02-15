import Foundation

protocol SearchGmailUseCaseProtocol: Sendable {
    func execute(query: String) async throws -> [GmailMessageSummary]
}

final class SearchGmailUseCase: SearchGmailUseCaseProtocol, @unchecked Sendable {
    private let repository: GmailRepositoryProtocol

    init(repository: GmailRepositoryProtocol) {
        self.repository = repository
    }

    func execute(query: String) async throws -> [GmailMessageSummary] {
        try await repository.search(query: query)
    }
}
