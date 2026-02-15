import Foundation

/// Use case for signing in with Gmail scopes
protocol SignInWithGmailUseCaseProtocol: Sendable {
    func execute() async throws -> User
}

final class SignInWithGmailUseCase: SignInWithGmailUseCaseProtocol, @unchecked Sendable {
    private let authRepository: AuthRepositoryProtocol

    init(authRepository: AuthRepositoryProtocol) {
        self.authRepository = authRepository
    }

    func execute() async throws -> User {
        try await authRepository.signInWithGmail()
    }
}
