import Foundation

protocol SendGmailMessageUseCaseProtocol: Sendable {
    func execute(
        to: String,
        subject: String,
        body: String,
        cc: String?,
        bcc: String?,
        html: Bool
    ) async throws -> GmailSendResponseDTO
}

final class SendGmailMessageUseCase: SendGmailMessageUseCaseProtocol, @unchecked Sendable {
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
        html: Bool
    ) async throws -> GmailSendResponseDTO {
        try await repository.sendMessage(
            to: to,
            subject: subject,
            body: body,
            cc: cc,
            bcc: bcc,
            html: html
        )
    }
}
