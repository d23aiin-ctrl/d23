import Foundation
import SwiftUI
import Combine

/// ViewModel for Gmail inbox and compose operations
@MainActor
final class GmailViewModel: ObservableObject {
    // MARK: - Published Properties

    @Published var emails: [GmailMessageSummary] = []
    @Published var selectedEmail: GmailMessageDetail?
    @Published var isLoading = false
    @Published var isLoadingDetail = false
    @Published var searchText = ""
    @Published var error: String?
    @Published var sendSuccess = false
    @Published var isSending = false

    // MARK: - Use Cases

    private let searchUseCase: SearchGmailUseCaseProtocol
    private let getMessageUseCase: GetGmailMessageUseCaseProtocol
    private let sendMessageUseCase: SendGmailMessageUseCaseProtocol
    private let scheduleEmailUseCase: ScheduleEmailUseCaseProtocol

    // MARK: - Init

    init(
        searchUseCase: SearchGmailUseCaseProtocol,
        getMessageUseCase: GetGmailMessageUseCaseProtocol,
        sendMessageUseCase: SendGmailMessageUseCaseProtocol,
        scheduleEmailUseCase: ScheduleEmailUseCaseProtocol
    ) {
        self.searchUseCase = searchUseCase
        self.getMessageUseCase = getMessageUseCase
        self.sendMessageUseCase = sendMessageUseCase
        self.scheduleEmailUseCase = scheduleEmailUseCase
    }

    // MARK: - Computed

    var filteredEmails: [GmailMessageSummary] {
        guard !searchText.isEmpty else { return emails }
        let query = searchText.lowercased()
        return emails.filter {
            $0.subject.lowercased().contains(query) ||
            $0.from.lowercased().contains(query) ||
            $0.snippet.lowercased().contains(query)
        }
    }

    // MARK: - Methods

    func loadInbox() async {
        await searchEmails(query: "in:inbox")
    }

    func searchEmails(query: String? = nil) async {
        let effectiveQuery = query ?? (searchText.isEmpty ? "in:inbox" : searchText)
        isLoading = true
        error = nil

        do {
            emails = try await searchUseCase.execute(query: effectiveQuery)
        } catch {
            self.error = error.localizedDescription
        }

        isLoading = false
    }

    func getEmailDetail(id: String) async {
        isLoadingDetail = true
        error = nil

        do {
            selectedEmail = try await getMessageUseCase.execute(id: id)
        } catch {
            self.error = error.localizedDescription
        }

        isLoadingDetail = false
    }

    func sendEmail(
        to: String,
        subject: String,
        body: String,
        cc: String?,
        bcc: String?
    ) async {
        isSending = true
        error = nil
        sendSuccess = false

        do {
            _ = try await sendMessageUseCase.execute(
                to: to,
                subject: subject,
                body: body,
                cc: cc,
                bcc: bcc,
                html: false
            )
            sendSuccess = true
        } catch {
            self.error = error.localizedDescription
        }

        isSending = false
    }

    func scheduleEmail(
        to: String,
        subject: String,
        body: String,
        cc: String?,
        bcc: String?,
        scheduledAt: Date
    ) async {
        isSending = true
        error = nil
        sendSuccess = false

        let formatter = ISO8601DateFormatter()
        formatter.formatOptions = [.withInternetDateTime]
        let dateString = formatter.string(from: scheduledAt)
        let timezone = TimeZone.current.identifier

        do {
            _ = try await scheduleEmailUseCase.execute(
                to: to,
                subject: subject,
                body: body,
                cc: cc,
                bcc: bcc,
                scheduledAt: dateString,
                timezone: timezone
            )
            sendSuccess = true
        } catch {
            self.error = error.localizedDescription
        }

        isSending = false
    }
}
