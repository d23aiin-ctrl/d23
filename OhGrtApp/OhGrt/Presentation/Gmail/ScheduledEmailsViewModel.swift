import Foundation
import SwiftUI
import Combine

/// ViewModel for managing scheduled emails
@MainActor
final class ScheduledEmailsViewModel: ObservableObject {
    // MARK: - Published Properties

    @Published var scheduledEmails: [ScheduledEmail] = []
    @Published var isLoading = false
    @Published var selectedStatus: ScheduledEmailStatus? = nil
    @Published var error: String?

    // MARK: - Use Cases

    private let getScheduledEmailsUseCase: GetScheduledEmailsUseCaseProtocol
    private let updateScheduledEmailUseCase: UpdateScheduledEmailUseCaseProtocol
    private let deleteScheduledEmailUseCase: DeleteScheduledEmailUseCaseProtocol

    // MARK: - Init

    init(
        getScheduledEmailsUseCase: GetScheduledEmailsUseCaseProtocol,
        updateScheduledEmailUseCase: UpdateScheduledEmailUseCaseProtocol,
        deleteScheduledEmailUseCase: DeleteScheduledEmailUseCaseProtocol
    ) {
        self.getScheduledEmailsUseCase = getScheduledEmailsUseCase
        self.updateScheduledEmailUseCase = updateScheduledEmailUseCase
        self.deleteScheduledEmailUseCase = deleteScheduledEmailUseCase
    }

    // MARK: - Computed

    var filteredEmails: [ScheduledEmail] {
        guard let status = selectedStatus else { return scheduledEmails }
        return scheduledEmails.filter { $0.status == status }
    }

    var activeCount: Int {
        scheduledEmails.filter { $0.status == .active }.count
    }

    var completedCount: Int {
        scheduledEmails.filter { $0.status == .completed }.count
    }

    var cancelledCount: Int {
        scheduledEmails.filter { $0.status == .cancelled }.count
    }

    // MARK: - Methods

    func loadEmails() async {
        isLoading = true
        error = nil

        do {
            scheduledEmails = try await getScheduledEmailsUseCase.execute(status: selectedStatus?.rawValue)
        } catch {
            self.error = error.localizedDescription
        }

        isLoading = false
    }

    func updateEmail(
        id: String,
        to: String? = nil,
        subject: String? = nil,
        body: String? = nil,
        scheduledAt: String? = nil
    ) async {
        error = nil

        do {
            let updated = try await updateScheduledEmailUseCase.execute(
                id: id,
                to: to,
                subject: subject,
                body: body,
                scheduledAt: scheduledAt
            )
            if let index = scheduledEmails.firstIndex(where: { $0.id == id }) {
                scheduledEmails[index] = updated
            }
        } catch {
            self.error = error.localizedDescription
        }
    }

    func cancelEmail(id: String) async {
        error = nil

        do {
            try await deleteScheduledEmailUseCase.execute(id: id)
            scheduledEmails.removeAll { $0.id == id }
        } catch {
            self.error = error.localizedDescription
        }
    }
}
