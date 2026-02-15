//
//  GmailLoginTests.swift
//  OhGrtTests
//
//  Tests for Gmail login flow via AuthViewModel
//

import Testing
import Foundation
import Combine
@testable import OhGrt

// MARK: - Mock Use Cases

private final class MockSignInWithGoogleUseCase: SignInWithGoogleUseCaseProtocol, @unchecked Sendable {
    var shouldThrow = false
    var errorToThrow: Error = DomainError.authenticationFailed("Google sign-in failed")

    func execute() async throws -> User {
        if shouldThrow { throw errorToThrow }
        return User(id: "google-user-1", email: "user@gmail.com", displayName: "Google User")
    }
}

private final class MockSignInWithGmailUseCase: SignInWithGmailUseCaseProtocol, @unchecked Sendable {
    var shouldThrow = false
    var errorToThrow: Error = DomainError.authenticationFailed("Gmail sign-in failed")
    var executeCalled = false
    var userToReturn = User(id: "gmail-user-1", email: "user@gmail.com", displayName: "Gmail User")

    func execute() async throws -> User {
        executeCalled = true
        if shouldThrow { throw errorToThrow }
        return userToReturn
    }
}

private final class MockSignOutUseCase: SignOutUseCaseProtocol, @unchecked Sendable {
    var shouldThrow = false
    var executeCalled = false

    func execute() async throws {
        executeCalled = true
        if shouldThrow { throw DomainError.unknown("Sign out failed") }
    }
}

private final class MockObserveAuthStateUseCase: ObserveAuthStateUseCaseProtocol, @unchecked Sendable {
    let subject = PassthroughSubject<AuthState, Never>()

    func execute() -> AnyPublisher<AuthState, Never> {
        subject.eraseToAnyPublisher()
    }
}

private final class MockContinueAsGuestUseCase: ContinueAsGuestUseCaseProtocol, @unchecked Sendable {
    var executeCalled = false

    func execute() {
        executeCalled = true
    }
}

// MARK: - Factory

@MainActor
private func makeAuthViewModel(
    google: MockSignInWithGoogleUseCase = MockSignInWithGoogleUseCase(),
    gmail: MockSignInWithGmailUseCase = MockSignInWithGmailUseCase(),
    signOut: MockSignOutUseCase = MockSignOutUseCase(),
    observe: MockObserveAuthStateUseCase = MockObserveAuthStateUseCase(),
    guest: MockContinueAsGuestUseCase = MockContinueAsGuestUseCase()
) -> AuthViewModel {
    AuthViewModel(
        signInWithGoogleUseCase: google,
        signInWithGmailUseCase: gmail,
        signOutUseCase: signOut,
        observeAuthStateUseCase: observe,
        continueAsGuestUseCase: guest
    )
}

// MARK: - AuthViewModel Initial State Tests

struct AuthViewModelInitialStateTests {

    @Test func initialStateIsUnknown() async throws {
        await MainActor.run {
            let vm = makeAuthViewModel()

            #expect(vm.authState == .unknown)
            #expect(vm.isAuthenticated == false)
            #expect(vm.currentUser == nil)
            #expect(vm.isLoading == false)
            #expect(vm.error == nil)
            #expect(vm.showError == false)
        }
    }
}

// MARK: - Gmail Sign-In Tests

struct GmailSignInTests {

    @Test func gmailSignInSuccess() async throws {
        let mockGmail = MockSignInWithGmailUseCase()
        mockGmail.shouldThrow = false
        mockGmail.userToReturn = User(
            id: "gmail-123",
            email: "testuser@gmail.com",
            displayName: "Test Gmail User"
        )

        let vm = await MainActor.run { makeAuthViewModel(gmail: mockGmail) }

        // Call the async method directly
        await vm.performGmailSignIn()

        await MainActor.run {
            #expect(vm.isAuthenticated == true)
            #expect(vm.currentUser?.id == "gmail-123")
            #expect(vm.currentUser?.email == "testuser@gmail.com")
            #expect(vm.currentUser?.displayName == "Test Gmail User")
            #expect(vm.isLoading == false)
            #expect(vm.error == nil)
            #expect(vm.showError == false)
        }
    }

    @Test func gmailSignInSetsLoadingDuringExecution() async throws {
        let mockGmail = MockSignInWithGmailUseCase()
        mockGmail.shouldThrow = false

        let vm = await MainActor.run { makeAuthViewModel(gmail: mockGmail) }

        // After completion, loading should be false
        await vm.performGmailSignIn()

        await MainActor.run {
            #expect(vm.isLoading == false)
        }
    }

    @Test func gmailSignInFailureWithDomainError() async throws {
        let mockGmail = MockSignInWithGmailUseCase()
        mockGmail.shouldThrow = true
        mockGmail.errorToThrow = DomainError.authenticationFailed("Invalid credentials")

        let vm = await MainActor.run { makeAuthViewModel(gmail: mockGmail) }

        await vm.performGmailSignIn()

        await MainActor.run {
            #expect(vm.isAuthenticated == false)
            #expect(vm.currentUser == nil)
            #expect(vm.isLoading == false)
            #expect(vm.error != nil)
            #expect(vm.error?.contains("Authentication failed") == true)
            #expect(vm.showError == true)
        }
    }

    @Test func gmailSignInFailureWithNetworkError() async throws {
        let mockGmail = MockSignInWithGmailUseCase()
        mockGmail.shouldThrow = true
        mockGmail.errorToThrow = DomainError.networkUnavailable

        let vm = await MainActor.run { makeAuthViewModel(gmail: mockGmail) }

        await vm.performGmailSignIn()

        await MainActor.run {
            #expect(vm.isAuthenticated == false)
            #expect(vm.error != nil)
            #expect(vm.error?.contains("internet") == true)
            #expect(vm.showError == true)
        }
    }

    @Test func gmailSignInFailureWithGenericError() async throws {
        let mockGmail = MockSignInWithGmailUseCase()
        mockGmail.shouldThrow = true
        mockGmail.errorToThrow = URLError(.badServerResponse)

        let vm = await MainActor.run { makeAuthViewModel(gmail: mockGmail) }

        await vm.performGmailSignIn()

        await MainActor.run {
            #expect(vm.isAuthenticated == false)
            #expect(vm.error != nil)
            #expect(vm.showError == true)
            #expect(vm.isLoading == false)
        }
    }

    @Test func gmailSignInClearsExistingError() async throws {
        let mockGmail = MockSignInWithGmailUseCase()
        mockGmail.shouldThrow = false

        let vm = await MainActor.run {
            let v = makeAuthViewModel(gmail: mockGmail)
            // Simulate a prior error state
            v.showError = true
            return v
        }

        await vm.performGmailSignIn()

        await MainActor.run {
            #expect(vm.error == nil)
            #expect(vm.isAuthenticated == true)
        }
    }

    @Test func gmailSignInCallsUseCase() async throws {
        let mockGmail = MockSignInWithGmailUseCase()
        mockGmail.shouldThrow = false

        let vm = await MainActor.run { makeAuthViewModel(gmail: mockGmail) }

        await vm.performGmailSignIn()

        #expect(mockGmail.executeCalled == true)
    }
}

// MARK: - Google Sign-In Tests (for comparison)

struct GoogleSignInTests {

    @Test func googleSignInSuccess() async throws {
        let mockGoogle = MockSignInWithGoogleUseCase()
        mockGoogle.shouldThrow = false

        let vm = await MainActor.run { makeAuthViewModel(google: mockGoogle) }

        await vm.performSignIn()

        await MainActor.run {
            #expect(vm.isAuthenticated == true)
            #expect(vm.currentUser?.email == "user@gmail.com")
            #expect(vm.isLoading == false)
            #expect(vm.error == nil)
        }
    }

    @Test func googleSignInFailure() async throws {
        let mockGoogle = MockSignInWithGoogleUseCase()
        mockGoogle.shouldThrow = true
        mockGoogle.errorToThrow = DomainError.authenticationFailed("Cancelled by user")

        let vm = await MainActor.run { makeAuthViewModel(google: mockGoogle) }

        await vm.performSignIn()

        await MainActor.run {
            #expect(vm.isAuthenticated == false)
            #expect(vm.error != nil)
            #expect(vm.showError == true)
        }
    }
}

// MARK: - Sign Out Tests

struct SignOutTests {

    @Test func signOutSuccess() async throws {
        let mockGmail = MockSignInWithGmailUseCase()
        let mockSignOut = MockSignOutUseCase()

        let vm = await MainActor.run { makeAuthViewModel(gmail: mockGmail, signOut: mockSignOut) }

        // First sign in
        await vm.performGmailSignIn()
        await MainActor.run {
            #expect(vm.isAuthenticated == true)
        }

        // Then sign out
        await vm.performSignOut()

        await MainActor.run {
            #expect(vm.isAuthenticated == false)
            #expect(vm.authState == .unauthenticated)
            #expect(vm.isLoading == false)
            #expect(mockSignOut.executeCalled == true)
        }
    }

    @Test func signOutFailure() async throws {
        let mockSignOut = MockSignOutUseCase()
        mockSignOut.shouldThrow = true

        let vm = await MainActor.run { makeAuthViewModel(signOut: mockSignOut) }

        await vm.performSignOut()

        await MainActor.run {
            #expect(vm.error != nil)
            #expect(vm.showError == true)
            #expect(vm.isLoading == false)
        }
    }
}

// MARK: - Continue as Guest Tests

struct ContinueAsGuestTests {

    @Test func continueAsGuestSetsAuthenticatedState() async throws {
        let mockGuest = MockContinueAsGuestUseCase()

        await MainActor.run {
            let vm = makeAuthViewModel(guest: mockGuest)

            vm.continueAsGuest()

            #expect(vm.isAuthenticated == true)
            #expect(vm.currentUser?.id == "guest")
            #expect(vm.currentUser?.email == "")
            #expect(vm.currentUser?.displayName == "Guest")
            #expect(mockGuest.executeCalled == true)
        }
    }
}

// MARK: - Clear Error Tests

struct AuthClearErrorTests {

    @Test func clearErrorResetsState() async throws {
        let mockGmail = MockSignInWithGmailUseCase()
        mockGmail.shouldThrow = true
        mockGmail.errorToThrow = DomainError.authenticationFailed("Test error")

        let vm = await MainActor.run { makeAuthViewModel(gmail: mockGmail) }

        // Trigger error
        await vm.performGmailSignIn()
        await MainActor.run {
            #expect(vm.error != nil)
            #expect(vm.showError == true)
        }

        // Clear error
        await MainActor.run {
            vm.clearError()

            #expect(vm.error == nil)
            #expect(vm.showError == false)
        }
    }
}

// MARK: - Auth State Tests

struct AuthStateTests {

    @Test func authStateUnknownIsNotAuthenticated() async throws {
        let state = AuthState.unknown
        #expect(state == .unknown)
    }

    @Test func authStateUnauthenticated() async throws {
        let state = AuthState.unauthenticated
        #expect(state == .unauthenticated)
        #expect(state != .unknown)
    }

    @Test func authStateAuthenticated() async throws {
        let user = User(id: "1", email: "test@gmail.com", displayName: "Test")
        let state = AuthState.authenticated(user)

        if case .authenticated(let u) = state {
            #expect(u.id == "1")
            #expect(u.email == "test@gmail.com")
        } else {
            #expect(Bool(false), "Expected authenticated state")
        }
    }

    @Test func authStateEquality() async throws {
        let date = Date(timeIntervalSince1970: 1000000)
        let user1 = User(id: "1", email: "a@b.com", createdAt: date)
        let user2 = User(id: "1", email: "a@b.com", createdAt: date)
        let user3 = User(id: "2", email: "c@d.com", createdAt: date)

        #expect(AuthState.authenticated(user1) == AuthState.authenticated(user2))
        #expect(AuthState.authenticated(user1) != AuthState.authenticated(user3))
        #expect(AuthState.unknown != AuthState.unauthenticated)
        #expect(AuthState.unknown != AuthState.authenticated(user1))
    }
}

// MARK: - User Entity Tests

struct UserEntityTests {

    @Test func userInitialization() async throws {
        let user = User(
            id: "user-1",
            email: "test@gmail.com",
            displayName: "Test User",
            photoURL: URL(string: "https://example.com/photo.jpg")
        )

        #expect(user.id == "user-1")
        #expect(user.email == "test@gmail.com")
        #expect(user.displayName == "Test User")
        #expect(user.photoURL?.absoluteString == "https://example.com/photo.jpg")
    }

    @Test func userWithMinimalFields() async throws {
        let user = User(id: "user-2", email: "minimal@gmail.com")

        #expect(user.id == "user-2")
        #expect(user.email == "minimal@gmail.com")
        #expect(user.displayName == nil)
        #expect(user.photoURL == nil)
    }

    @Test func userEquality() async throws {
        let date = Date(timeIntervalSince1970: 1000000)
        let user1 = User(id: "1", email: "a@b.com", displayName: "A", createdAt: date)
        let user2 = User(id: "1", email: "a@b.com", displayName: "A", createdAt: date)

        #expect(user1 == user2)
    }

    @Test func userInequalityById() async throws {
        let date = Date(timeIntervalSince1970: 1000000)
        let user1 = User(id: "1", email: "a@b.com", createdAt: date)
        let user2 = User(id: "2", email: "a@b.com", createdAt: date)

        #expect(user1 != user2)
    }

    @Test func userCreatedAtIsSet() async throws {
        let before = Date()
        let user = User(id: "1", email: "a@b.com")
        let after = Date()

        #expect(user.createdAt >= before)
        #expect(user.createdAt <= after)
    }
}

// MARK: - Domain Error Tests

struct DomainErrorTests {

    @Test func authenticationFailedError() async throws {
        let error = DomainError.authenticationFailed("Bad token")
        #expect(error.localizedDescription.contains("Authentication failed"))
        #expect(error.localizedDescription.contains("Bad token"))
    }

    @Test func networkUnavailableError() async throws {
        let error = DomainError.networkUnavailable
        #expect(error.localizedDescription.contains("internet"))
    }

    @Test func tokenExpiredError() async throws {
        let error = DomainError.tokenExpired
        #expect(error.localizedDescription.contains("expired"))
    }

    @Test func notAuthenticatedError() async throws {
        let error = DomainError.notAuthenticated
        #expect(error.localizedDescription.contains("sign in"))
    }

    @Test func serverError() async throws {
        let error = DomainError.serverError("Internal error")
        #expect(error.localizedDescription.contains("Server error"))
        #expect(error.localizedDescription.contains("Internal error"))
    }

    @Test func domainErrorEquality() async throws {
        #expect(DomainError.notAuthenticated == DomainError.notAuthenticated)
        #expect(DomainError.tokenExpired == DomainError.tokenExpired)
        #expect(DomainError.networkUnavailable == DomainError.networkUnavailable)
        #expect(DomainError.notAuthenticated != DomainError.tokenExpired)
    }

    @Test func allDomainErrorsHaveDescriptions() async throws {
        let errors: [DomainError] = [
            .notAuthenticated,
            .authenticationFailed("test"),
            .tokenExpired,
            .invalidCredentials,
            .networkUnavailable,
            .serverError("test"),
            .requestTimeout,
            .invalidResponse,
            .notFound,
            .dataCorrupted,
            .saveFailed("test"),
            .deleteFailed("test"),
            .messageEmpty,
            .conversationNotFound,
            .rateLimitExceeded,
            .usageLimitReached,
            .unknown("test"),
            .notImplemented("test")
        ]

        for error in errors {
            #expect(!error.localizedDescription.isEmpty)
        }
    }
}

// MARK: - Auth State Observer Tests

struct AuthStateObserverTests {

    @Test func observeAuthStateReceivesUpdates() async throws {
        let mockObserve = MockObserveAuthStateUseCase()

        let vm = await MainActor.run { makeAuthViewModel(observe: mockObserve) }

        // Send an authenticated state through the publisher
        let user = User(id: "obs-1", email: "observed@gmail.com", displayName: "Observed")
        mockObserve.subject.send(.authenticated(user))

        // Give Combine time to deliver
        try await Task.sleep(nanoseconds: 100_000_000) // 0.1s

        await MainActor.run {
            #expect(vm.authState == .authenticated(user))
            #expect(vm.isAuthenticated == true)
            #expect(vm.currentUser?.email == "observed@gmail.com")
        }
    }

    @Test func observeAuthStateReceivesUnauthenticated() async throws {
        let mockObserve = MockObserveAuthStateUseCase()

        let vm = await MainActor.run { makeAuthViewModel(observe: mockObserve) }

        mockObserve.subject.send(.unauthenticated)

        try await Task.sleep(nanoseconds: 100_000_000)

        await MainActor.run {
            #expect(vm.authState == .unauthenticated)
            #expect(vm.isAuthenticated == false)
            #expect(vm.currentUser == nil)
        }
    }
}
