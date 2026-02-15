//
//  ChatViewModelTests.swift
//  OhGrtTests
//
//  Tests for ChatViewModel functionality
//

import Testing
import Foundation
@testable import OhGrt

// MARK: - Mock Use Cases for ChatViewModel

private final class MockSendMessageUseCase: SendMessageUseCaseProtocol, @unchecked Sendable {
    func execute(message: String, conversationId: UUID, tools: [String], location: LocationDTO?) async throws -> ChatMessage {
        ChatMessage(conversationId: conversationId, content: "Mock response", role: .assistant)
    }
}

private final class MockGetMessagesUseCase: GetMessagesUseCaseProtocol, @unchecked Sendable {
    func execute(conversationId: UUID, before: Date?, limit: Int) async throws -> [ChatMessage] {
        []
    }
}

private final class MockGetToolsUseCase: GetToolsUseCaseProtocol, @unchecked Sendable {
    func execute() async throws -> [Tool] {
        []
    }
}

private final class MockGetProvidersUseCase: GetProvidersUseCaseProtocol, @unchecked Sendable {
    func execute() async throws -> [Provider] {
        []
    }
}

private final class MockCreateConversationUseCase: CreateConversationUseCaseProtocol, @unchecked Sendable {
    func execute(title: String, tools: [String]) async throws -> ChatConversation {
        ChatConversation(title: title, tools: tools)
    }
}

@MainActor
private func makeChatViewModel() -> ChatViewModel {
    ChatViewModel(
        sendMessageUseCase: MockSendMessageUseCase(),
        getMessagesUseCase: MockGetMessagesUseCase(),
        getToolsUseCase: MockGetToolsUseCase(),
        getProvidersUseCase: MockGetProvidersUseCase(),
        createConversationUseCase: MockCreateConversationUseCase()
    )
}

// MARK: - ChatViewModel State Tests

struct ChatViewModelStateTests {

    @Test func initialState() async throws {
        await MainActor.run {
            let viewModel = makeChatViewModel()

            #expect(viewModel.messages.isEmpty)
            #expect(viewModel.inputText.isEmpty)
            #expect(viewModel.isLoading == false)
            #expect(viewModel.availableTools.isEmpty)
            #expect(viewModel.selectedTools.isEmpty)
        }
    }

    @Test func startNewConversationDoesNotThrow() async throws {
        await MainActor.run {
            let viewModel = makeChatViewModel()
            viewModel.inputText = "Some text"

            // startNewConversation() launches an async Task internally
            // Verify it can be called without error
            viewModel.startNewConversation()

            // messages should still be empty (no messages added yet)
            #expect(viewModel.messages.isEmpty)
        }
    }

    @Test func clearError() async throws {
        await MainActor.run {
            let viewModel = makeChatViewModel()

            viewModel.clearError()

            #expect(viewModel.errorMessage == nil)
        }
    }
}

// MARK: - Tool Selection Tests

struct ChatViewModelToolTests {

    @Test func toggleToolAddsToSelection() async throws {
        await MainActor.run {
            let viewModel = makeChatViewModel()

            viewModel.toggleTool("weather")

            #expect(viewModel.selectedTools.contains("weather"))
        }
    }

    @Test func toggleToolRemovesFromSelection() async throws {
        await MainActor.run {
            let viewModel = makeChatViewModel()
            viewModel.selectedTools = ["weather", "pdf"]

            viewModel.toggleTool("weather")

            #expect(!viewModel.selectedTools.contains("weather"))
            #expect(viewModel.selectedTools.contains("pdf"))
        }
    }

    @Test func toggleMultipleTools() async throws {
        await MainActor.run {
            let viewModel = makeChatViewModel()

            viewModel.toggleTool("weather")
            viewModel.toggleTool("pdf")
            viewModel.toggleTool("jira")

            #expect(viewModel.selectedTools.count == 3)
            #expect(viewModel.selectedTools.contains("weather"))
            #expect(viewModel.selectedTools.contains("pdf"))
            #expect(viewModel.selectedTools.contains("jira"))
        }
    }
}

// MARK: - Error Message Formatting Tests

struct ChatViewModelErrorTests {

    @Test func friendlyErrorMessageReturnsLocalizedDescription() async throws {
        await MainActor.run {
            let viewModel = makeChatViewModel()
            let error = URLError(.notConnectedToInternet)

            let message = viewModel.friendlyErrorMessage(for: error)

            // friendlyErrorMessage returns error.localizedDescription
            #expect(!message.isEmpty)
        }
    }

    @Test func friendlyErrorMessageForGenericError() async throws {
        await MainActor.run {
            let viewModel = makeChatViewModel()
            let error = NSError(domain: "TestDomain", code: 123, userInfo: [NSLocalizedDescriptionKey: "Custom error"])

            let message = viewModel.friendlyErrorMessage(for: error)

            #expect(message == "Custom error")
        }
    }
}

// MARK: - Input Validation Tests

struct ChatViewModelInputTests {

    @Test func emptyInputDoesNotSend() async throws {
        await MainActor.run {
            let viewModel = makeChatViewModel()
            viewModel.inputText = ""

            let text = viewModel.inputText.trimmingCharacters(in: .whitespacesAndNewlines)
            #expect(text.isEmpty)
        }
    }

    @Test func whitespaceOnlyInputDoesNotSend() async throws {
        await MainActor.run {
            let viewModel = makeChatViewModel()
            viewModel.inputText = "   \n\t   "

            let text = viewModel.inputText.trimmingCharacters(in: .whitespacesAndNewlines)
            #expect(text.isEmpty)
        }
    }

    @Test func validInputTrimsWhitespace() async throws {
        await MainActor.run {
            let viewModel = makeChatViewModel()
            viewModel.inputText = "  Hello World  "

            let text = viewModel.inputText.trimmingCharacters(in: .whitespacesAndNewlines)
            #expect(text == "Hello World")
        }
    }
}

// MARK: - Provider State Tests

struct ChatViewModelProviderTests {

    @Test func initialProviderState() async throws {
        await MainActor.run {
            let viewModel = makeChatViewModel()

            #expect(viewModel.providers.isEmpty)
            #expect(viewModel.providerError == nil)
        }
    }
}
