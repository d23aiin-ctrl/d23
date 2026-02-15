import Foundation

/// Use case for continuing without authentication
protocol ContinueAsGuestUseCaseProtocol: Sendable {
    func execute()
}

final class ContinueAsGuestUseCase: ContinueAsGuestUseCaseProtocol, @unchecked Sendable {
    private let authRepository: AuthRepositoryProtocol

    init(authRepository: AuthRepositoryProtocol) {
        self.authRepository = authRepository
    }

    func execute() {
        authRepository.continueAsGuest()
    }
}
