import Foundation
import Combine
import SwiftUI

/// ViewModel for authentication screens
@MainActor
final class AuthViewModel: ObservableObject {
    // MARK: - Published Properties

    @Published private(set) var authState: AuthState = .unknown
    @Published private(set) var isLoading = false
    @Published private(set) var error: String?
    @Published var showError = false

    // MARK: - Use Cases

    private let signInWithGoogleUseCase: SignInWithGoogleUseCaseProtocol
    private let signInWithGmailUseCase: SignInWithGmailUseCaseProtocol
    private let signOutUseCase: SignOutUseCaseProtocol
    private let observeAuthStateUseCase: ObserveAuthStateUseCaseProtocol
    private let continueAsGuestUseCase: ContinueAsGuestUseCaseProtocol

    // MARK: - Private Properties

    private var cancellables = Set<AnyCancellable>()

    // MARK: - Computed Properties

    var isAuthenticated: Bool {
        if case .authenticated = authState {
            return true
        }
        return false
    }

    var currentUser: User? {
        if case .authenticated(let user) = authState {
            return user
        }
        return nil
    }

    // MARK: - Initialization

    init(
        signInWithGoogleUseCase: SignInWithGoogleUseCaseProtocol,
        signInWithGmailUseCase: SignInWithGmailUseCaseProtocol,
        signOutUseCase: SignOutUseCaseProtocol,
        observeAuthStateUseCase: ObserveAuthStateUseCaseProtocol,
        continueAsGuestUseCase: ContinueAsGuestUseCaseProtocol
    ) {
        self.signInWithGoogleUseCase = signInWithGoogleUseCase
        self.signInWithGmailUseCase = signInWithGmailUseCase
        self.signOutUseCase = signOutUseCase
        self.observeAuthStateUseCase = observeAuthStateUseCase
        self.continueAsGuestUseCase = continueAsGuestUseCase

        setupObservers()
    }

    // MARK: - Public Methods

    func signInWithGoogle() {
        Task {
            await performSignIn()
        }
    }

    func signOut() {
        Task {
            await performSignOut()
        }
    }

    func signInWithGmail() {
        Task {
            await performGmailSignIn()
        }
    }

    func continueAsGuest() {
        continueAsGuestUseCase.execute()
        authState = .authenticated(
            User(id: "guest", email: "", displayName: "Guest", photoURL: nil)
        )
    }

    func clearError() {
        error = nil
        showError = false
    }

    // MARK: - Private Methods

    private func setupObservers() {
        observeAuthStateUseCase.execute()
            .receive(on: DispatchQueue.main)
            .sink { [weak self] state in
                self?.authState = state
            }
            .store(in: &cancellables)
    }

    func performSignIn() async {
        isLoading = true
        error = nil

        do {
            let user = try await signInWithGoogleUseCase.execute()
            authState = .authenticated(user)
        } catch let domainError as DomainError {
            error = domainError.localizedDescription
            showError = true
        } catch {
            self.error = error.localizedDescription
            showError = true
        }

        isLoading = false
    }

    func performGmailSignIn() async {
        isLoading = true
        error = nil

        do {
            let user = try await signInWithGmailUseCase.execute()
            authState = .authenticated(user)
        } catch let domainError as DomainError {
            error = domainError.localizedDescription
            showError = true
        } catch {
            self.error = error.localizedDescription
            showError = true
        }

        isLoading = false
    }

    func performSignOut() async {
        isLoading = true

        do {
            try await signOutUseCase.execute()
            authState = .unauthenticated
        } catch let domainError as DomainError {
            error = domainError.localizedDescription
            showError = true
        } catch {
            self.error = error.localizedDescription
            showError = true
        }

        isLoading = false
    }
}
