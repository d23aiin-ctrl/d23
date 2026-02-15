//
//  GmailFeatureTests.swift
//  OhGrtTests
//
//  Tests for Gmail feature: DTOs, Entities, Mappers, ViewModels, Endpoints
//

import Testing
import Foundation
@testable import OhGrt

// MARK: - Gmail DTO Tests

struct GmailDTOTests {

    @Test func gmailSearchResponseDecoding() async throws {
        let json = """
        {
            "emails": [
                {"id": "msg1", "snippet": "Hello there", "subject": "Meeting", "from": "alice@test.com", "date": "2025-06-15"},
                {"id": "msg2", "snippet": "Update", "subject": "Report", "from": "bob@test.com", "date": "2025-06-14"}
            ]
        }
        """.data(using: .utf8)!

        let response = try JSONDecoder().decode(GmailSearchResponseDTO.self, from: json)
        #expect(response.emails.count == 2)
        #expect(response.emails[0].id == "msg1")
        #expect(response.emails[0].subject == "Meeting")
        #expect(response.emails[1].from == "bob@test.com")
    }

    @Test func gmailMessageSummaryDTOWithNilFields() async throws {
        let json = """
        {"id": "msg1"}
        """.data(using: .utf8)!

        let dto = try JSONDecoder().decode(GmailMessageSummaryDTO.self, from: json)
        #expect(dto.id == "msg1")
        #expect(dto.snippet == nil)
        #expect(dto.subject == nil)
        #expect(dto.from == nil)
        #expect(dto.date == nil)
    }

    @Test func gmailMessageDetailDTODecoding() async throws {
        let json = """
        {
            "id": "detail1",
            "threadId": "thread1",
            "snippet": "Preview text",
            "subject": "Important",
            "from": "sender@test.com",
            "to": "receiver@test.com",
            "cc": "cc@test.com",
            "date": "2025-06-15T10:00:00Z",
            "body": "<html><body>Hello</body></html>",
            "labelIds": ["INBOX", "UNREAD"]
        }
        """.data(using: .utf8)!

        let dto = try JSONDecoder().decode(GmailMessageDetailDTO.self, from: json)
        #expect(dto.id == "detail1")
        #expect(dto.threadId == "thread1")
        #expect(dto.to == "receiver@test.com")
        #expect(dto.cc == "cc@test.com")
        #expect(dto.labelIds?.count == 2)
        #expect(dto.body?.contains("Hello") == true)
    }

    @Test func gmailSendRequestEncoding() async throws {
        let request = GmailSendRequestDTO(
            to: "user@test.com",
            subject: "Test",
            body: "Body text",
            cc: nil,
            bcc: nil,
            html: false
        )

        #expect(request.to == "user@test.com")
        #expect(request.subject == "Test")
        #expect(request.html == false)
        #expect(request.cc == nil)

        let data = try JSONEncoder().encode(request)
        let dict = try JSONSerialization.jsonObject(with: data) as! [String: Any]
        #expect(dict["to"] as? String == "user@test.com")
    }

    @Test func gmailSendResponseDecoding() async throws {
        let json = """
        {"success": true, "message_id": "abc123", "thread_id": "thread456"}
        """.data(using: .utf8)!

        let response = try JSONDecoder().decode(GmailSendResponseDTO.self, from: json)
        #expect(response.success == true)
        #expect(response.messageId == "abc123")
        #expect(response.threadId == "thread456")
    }

    @Test func gmailSendResponseDecodingMinimal() async throws {
        let json = """
        {"success": false}
        """.data(using: .utf8)!

        let response = try JSONDecoder().decode(GmailSendResponseDTO.self, from: json)
        #expect(response.success == false)
        #expect(response.messageId == nil)
        #expect(response.threadId == nil)
    }
}

// MARK: - Scheduled Email DTO Tests

struct ScheduledEmailDTOTests {

    @Test func scheduledEmailDTODecoding() async throws {
        let json = """
        {
            "id": "sched1",
            "to": "user@test.com",
            "subject": "Reminder",
            "body": "Don't forget",
            "cc": "cc@test.com",
            "bcc": null,
            "scheduled_at": "2025-06-20T09:00:00Z",
            "status": "active",
            "created_at": "2025-06-15T10:00:00Z",
            "last_run_at": null,
            "run_count": 0
        }
        """.data(using: .utf8)!

        let dto = try JSONDecoder().decode(ScheduledEmailDTO.self, from: json)
        #expect(dto.id == "sched1")
        #expect(dto.to == "user@test.com")
        #expect(dto.subject == "Reminder")
        #expect(dto.status == "active")
        #expect(dto.cc == "cc@test.com")
        #expect(dto.bcc == nil)
        #expect(dto.runCount == 0)
    }

    @Test func scheduleEmailRequestEncoding() async throws {
        let request = ScheduleEmailRequestDTO(
            to: "user@test.com",
            subject: "Test",
            body: "Body",
            cc: nil,
            bcc: nil,
            scheduledAt: "2025-06-20T09:00:00Z",
            timezone: "Asia/Kolkata"
        )

        let data = try JSONEncoder().encode(request)
        let dict = try JSONSerialization.jsonObject(with: data) as! [String: Any]
        #expect(dict["to"] as? String == "user@test.com")
        #expect(dict["scheduled_at"] as? String == "2025-06-20T09:00:00Z")
        #expect(dict["timezone"] as? String == "Asia/Kolkata")
    }

    @Test func updateScheduledEmailRequestEncoding() async throws {
        let request = UpdateScheduledEmailRequestDTO(
            to: "new@test.com",
            subject: "Updated",
            body: nil,
            scheduledAt: "2025-06-21T10:00:00Z"
        )

        let data = try JSONEncoder().encode(request)
        let dict = try JSONSerialization.jsonObject(with: data) as! [String: Any]
        #expect(dict["to"] as? String == "new@test.com")
        #expect(dict["subject"] as? String == "Updated")
        #expect(dict["scheduled_at"] as? String == "2025-06-21T10:00:00Z")
    }
}

// MARK: - Gmail Entity Tests

struct GmailMessageEntityTests {

    @Test func gmailMessageSummaryInit() async throws {
        let summary = GmailMessageSummary(
            id: "msg1",
            snippet: "Hello",
            subject: "Test Subject",
            from: "Alice <alice@test.com>",
            date: "2025-06-15"
        )

        #expect(summary.id == "msg1")
        #expect(summary.snippet == "Hello")
        #expect(summary.subject == "Test Subject")
        #expect(summary.from == "Alice <alice@test.com>")
    }

    @Test func gmailMessageSummaryEquality() async throws {
        let a = GmailMessageSummary(id: "1", snippet: "A", subject: "S", from: "f", date: "d")
        let b = GmailMessageSummary(id: "1", snippet: "A", subject: "S", from: "f", date: "d")
        let c = GmailMessageSummary(id: "2", snippet: "A", subject: "S", from: "f", date: "d")

        #expect(a == b)
        #expect(a != c)
    }

    @Test func gmailMessageSummaryHashable() async throws {
        let a = GmailMessageSummary(id: "1", snippet: "A", subject: "S", from: "f", date: "d")
        let b = GmailMessageSummary(id: "2", snippet: "B", subject: "T", from: "g", date: "e")
        let set: Set<GmailMessageSummary> = [a, b]
        #expect(set.count == 2)
    }

    @Test func gmailMessageDetailInit() async throws {
        let detail = GmailMessageDetail(
            id: "detail1",
            threadId: "thread1",
            snippet: "Preview",
            subject: "Important",
            from: "sender@test.com",
            to: "receiver@test.com",
            cc: "cc@test.com",
            date: "2025-06-15",
            body: "<html>Hello</html>",
            labelIds: ["INBOX", "UNREAD"]
        )

        #expect(detail.id == "detail1")
        #expect(detail.threadId == "thread1")
        #expect(detail.to == "receiver@test.com")
        #expect(detail.cc == "cc@test.com")
        #expect(detail.labelIds.count == 2)
    }

    @Test func gmailMessageDetailEquality() async throws {
        let a = GmailMessageDetail(id: "1", threadId: nil, snippet: "", subject: "", from: "", to: "", cc: nil, date: "", body: "", labelIds: [])
        let b = GmailMessageDetail(id: "1", threadId: nil, snippet: "", subject: "", from: "", to: "", cc: nil, date: "", body: "", labelIds: [])
        #expect(a == b)
    }
}

// MARK: - Scheduled Email Entity Tests

struct ScheduledEmailEntityTests {

    @Test func scheduledEmailInit() async throws {
        let email = ScheduledEmail(
            id: "sched1",
            to: "user@test.com",
            subject: "Reminder",
            body: "Body text",
            cc: nil,
            bcc: nil,
            scheduledAt: "2025-06-20T09:00:00Z",
            status: .active,
            createdAt: "2025-06-15",
            lastRunAt: nil,
            runCount: 0
        )

        #expect(email.id == "sched1")
        #expect(email.to == "user@test.com")
        #expect(email.status == .active)
        #expect(email.runCount == 0)
    }

    @Test func scheduledEmailEquality() async throws {
        let a = ScheduledEmail(id: "1", to: "a@t.com", subject: "S", body: "B", cc: nil, bcc: nil, scheduledAt: "t", status: .active, createdAt: nil, lastRunAt: nil, runCount: 0)
        let b = ScheduledEmail(id: "1", to: "a@t.com", subject: "S", body: "B", cc: nil, bcc: nil, scheduledAt: "t", status: .active, createdAt: nil, lastRunAt: nil, runCount: 0)
        let c = ScheduledEmail(id: "2", to: "a@t.com", subject: "S", body: "B", cc: nil, bcc: nil, scheduledAt: "t", status: .active, createdAt: nil, lastRunAt: nil, runCount: 0)

        #expect(a == b)
        #expect(a != c)
    }

    @Test func scheduledEmailStatusDisplayNames() async throws {
        #expect(ScheduledEmailStatus.active.displayName == "Scheduled")
        #expect(ScheduledEmailStatus.completed.displayName == "Sent")
        #expect(ScheduledEmailStatus.cancelled.displayName == "Cancelled")
        #expect(ScheduledEmailStatus.failed.displayName == "Failed")
    }

    @Test func scheduledEmailStatusRawValues() async throws {
        #expect(ScheduledEmailStatus.active.rawValue == "active")
        #expect(ScheduledEmailStatus.completed.rawValue == "completed")
        #expect(ScheduledEmailStatus.cancelled.rawValue == "cancelled")
        #expect(ScheduledEmailStatus.failed.rawValue == "failed")
    }

    @Test func scheduledEmailStatusCaseIterable() async throws {
        #expect(ScheduledEmailStatus.allCases.count == 4)
    }
}

// MARK: - Gmail Mapper Tests

struct GmailMapperTests {

    @Test func mapSummaryDTOToDomain() async throws {
        let dto = GmailMessageSummaryDTO(
            id: "msg1",
            snippet: "Hello",
            subject: "Test",
            from: "alice@test.com",
            date: "2025-06-15"
        )

        let domain = GmailMapper.toDomain(dto)

        #expect(domain.id == "msg1")
        #expect(domain.snippet == "Hello")
        #expect(domain.subject == "Test")
        #expect(domain.from == "alice@test.com")
        #expect(domain.date == "2025-06-15")
    }

    @Test func mapSummaryDTOWithNilsToDomain() async throws {
        let dto = GmailMessageSummaryDTO(
            id: "msg1",
            snippet: nil,
            subject: nil,
            from: nil,
            date: nil
        )

        let domain = GmailMapper.toDomain(dto)

        #expect(domain.id == "msg1")
        #expect(domain.snippet == "")
        #expect(domain.subject == "(No subject)")
        #expect(domain.from == "")
        #expect(domain.date == "")
    }

    @Test func mapDetailDTOToDomain() async throws {
        let dto = GmailMessageDetailDTO(
            id: "detail1",
            threadId: "thread1",
            snippet: "Preview",
            subject: "Important",
            from: "sender@test.com",
            to: "receiver@test.com",
            cc: "cc@test.com",
            date: "2025-06-15",
            body: "<html>Body</html>",
            labelIds: ["INBOX"]
        )

        let domain = GmailMapper.toDomain(dto)

        #expect(domain.id == "detail1")
        #expect(domain.threadId == "thread1")
        #expect(domain.subject == "Important")
        #expect(domain.to == "receiver@test.com")
        #expect(domain.cc == "cc@test.com")
        #expect(domain.body == "<html>Body</html>")
        #expect(domain.labelIds == ["INBOX"])
    }

    @Test func mapDetailDTOWithNilsToDomain() async throws {
        let dto = GmailMessageDetailDTO(
            id: "detail1",
            threadId: nil,
            snippet: nil,
            subject: nil,
            from: nil,
            to: nil,
            cc: nil,
            date: nil,
            body: nil,
            labelIds: nil
        )

        let domain = GmailMapper.toDomain(dto)

        #expect(domain.id == "detail1")
        #expect(domain.threadId == nil)
        #expect(domain.snippet == "")
        #expect(domain.subject == "(No subject)")
        #expect(domain.from == "")
        #expect(domain.to == "")
        #expect(domain.cc == nil)
        #expect(domain.body == "")
        #expect(domain.labelIds.isEmpty)
    }
}

// MARK: - Scheduled Email Mapper Tests

struct ScheduledEmailMapperTests {

    @Test func mapDTOToDomain() async throws {
        let dto = ScheduledEmailDTO(
            id: "sched1",
            to: "user@test.com",
            subject: "Reminder",
            body: "Don't forget",
            cc: "cc@test.com",
            bcc: nil,
            scheduledAt: "2025-06-20T09:00:00Z",
            status: "active",
            createdAt: "2025-06-15",
            lastRunAt: nil,
            runCount: 0
        )

        let domain = ScheduledEmailMapper.toDomain(dto)

        #expect(domain.id == "sched1")
        #expect(domain.to == "user@test.com")
        #expect(domain.subject == "Reminder")
        #expect(domain.status == .active)
        #expect(domain.cc == "cc@test.com")
        #expect(domain.bcc == nil)
        #expect(domain.runCount == 0)
    }

    @Test func mapDTOWithCompletedStatus() async throws {
        let dto = ScheduledEmailDTO(
            id: "sched2",
            to: "user@test.com",
            subject: "Done",
            body: "Body",
            cc: nil,
            bcc: nil,
            scheduledAt: "2025-06-20T09:00:00Z",
            status: "completed",
            createdAt: nil,
            lastRunAt: "2025-06-20T09:01:00Z",
            runCount: 1
        )

        let domain = ScheduledEmailMapper.toDomain(dto)
        #expect(domain.status == .completed)
        #expect(domain.runCount == 1)
        #expect(domain.lastRunAt == "2025-06-20T09:01:00Z")
    }

    @Test func mapDTOWithUnknownStatusDefaultsToActive() async throws {
        let dto = ScheduledEmailDTO(
            id: "sched3",
            to: "user@test.com",
            subject: "Test",
            body: "Body",
            cc: nil,
            bcc: nil,
            scheduledAt: "2025-06-20T09:00:00Z",
            status: "unknown_status",
            createdAt: nil,
            lastRunAt: nil,
            runCount: nil
        )

        let domain = ScheduledEmailMapper.toDomain(dto)
        #expect(domain.status == .active)
        #expect(domain.runCount == 0)
    }

    @Test func mapAllStatuses() async throws {
        let statuses = ["active", "completed", "cancelled", "failed"]
        let expected: [ScheduledEmailStatus] = [.active, .completed, .cancelled, .failed]

        for (statusStr, expectedStatus) in zip(statuses, expected) {
            let dto = ScheduledEmailDTO(
                id: "id",
                to: "t",
                subject: "s",
                body: "b",
                cc: nil,
                bcc: nil,
                scheduledAt: "t",
                status: statusStr,
                createdAt: nil,
                lastRunAt: nil,
                runCount: nil
            )
            let domain = ScheduledEmailMapper.toDomain(dto)
            #expect(domain.status == expectedStatus)
        }
    }
}

// MARK: - Gmail API Endpoint Tests

struct GmailEndpointTests {

    @Test func gmailSearchEndpoint() async throws {
        let endpoint = APIEndpoint.gmailSearch(query: "in:inbox")
        #expect(endpoint.path.contains("/gmail/search"))
        #expect(endpoint.path.contains("q="))
        #expect(endpoint.method == .get)
        #expect(endpoint.requiresAuth == true)
    }

    @Test func gmailMessageEndpoint() async throws {
        let endpoint = APIEndpoint.gmailMessage(id: "msg123")
        #expect(endpoint.path == "/gmail/messages/msg123")
        #expect(endpoint.method == .get)
        #expect(endpoint.requiresAuth == true)
    }

    @Test func gmailSendEndpoint() async throws {
        let endpoint = APIEndpoint.gmailSend
        #expect(endpoint.path == "/gmail/send")
        #expect(endpoint.method == .post)
        #expect(endpoint.requiresAuth == true)
    }

    @Test func emailScheduleEndpoint() async throws {
        let endpoint = APIEndpoint.emailSchedule
        #expect(endpoint.path == "/chat/email/schedule")
        #expect(endpoint.method == .post)
        #expect(endpoint.requiresAuth == true)
    }

    @Test func emailScheduledListEndpoint() async throws {
        let endpoint = APIEndpoint.emailScheduled(status: nil)
        #expect(endpoint.path.contains("/chat/email/scheduled"))
        #expect(endpoint.method == .get)
        #expect(endpoint.requiresAuth == true)
    }

    @Test func emailScheduledListWithStatusFilter() async throws {
        let endpoint = APIEndpoint.emailScheduled(status: "active")
        #expect(endpoint.path.contains("status=active"))
    }

    @Test func emailScheduledUpdateEndpoint() async throws {
        let endpoint = APIEndpoint.emailScheduledUpdate(id: "sched123")
        #expect(endpoint.path == "/chat/email/scheduled/sched123")
        #expect(endpoint.method == .put)
        #expect(endpoint.requiresAuth == true)
    }

    @Test func emailScheduledDeleteEndpoint() async throws {
        let endpoint = APIEndpoint.emailScheduledDelete(id: "sched456")
        #expect(endpoint.path == "/chat/email/scheduled/sched456")
        #expect(endpoint.method == .delete)
        #expect(endpoint.requiresAuth == true)
    }
}

// MARK: - Gmail ViewModel Tests

private final class MockSearchGmailUseCase: SearchGmailUseCaseProtocol, @unchecked Sendable {
    var result: [GmailMessageSummary] = []
    var shouldThrow = false

    func execute(query: String) async throws -> [GmailMessageSummary] {
        if shouldThrow { throw URLError(.badServerResponse) }
        return result
    }
}

private final class MockGetGmailMessageUseCase: GetGmailMessageUseCaseProtocol, @unchecked Sendable {
    var result: GmailMessageDetail?
    var shouldThrow = false

    func execute(id: String) async throws -> GmailMessageDetail {
        if shouldThrow { throw URLError(.badServerResponse) }
        return result!
    }
}

private final class MockSendGmailMessageUseCase: SendGmailMessageUseCaseProtocol, @unchecked Sendable {
    var shouldThrow = false

    func execute(to: String, subject: String, body: String, cc: String?, bcc: String?, html: Bool) async throws -> GmailSendResponseDTO {
        if shouldThrow { throw URLError(.badServerResponse) }
        return GmailSendResponseDTO(success: true, messageId: "sent1", threadId: "t1")
    }
}

private final class MockScheduleEmailUseCase: ScheduleEmailUseCaseProtocol, @unchecked Sendable {
    var shouldThrow = false

    func execute(to: String, subject: String, body: String, cc: String?, bcc: String?, scheduledAt: String, timezone: String) async throws -> GmailSendResponseDTO {
        if shouldThrow { throw URLError(.badServerResponse) }
        return GmailSendResponseDTO(success: true, messageId: "sched1", threadId: nil)
    }
}

struct GmailViewModelTests {

    @MainActor
    private func makeGmailViewModel(
        search: MockSearchGmailUseCase = MockSearchGmailUseCase(),
        getMessage: MockGetGmailMessageUseCase = MockGetGmailMessageUseCase(),
        sendMessage: MockSendGmailMessageUseCase = MockSendGmailMessageUseCase(),
        scheduleEmail: MockScheduleEmailUseCase = MockScheduleEmailUseCase()
    ) -> GmailViewModel {
        GmailViewModel(
            searchUseCase: search,
            getMessageUseCase: getMessage,
            sendMessageUseCase: sendMessage,
            scheduleEmailUseCase: scheduleEmail
        )
    }

    @Test func initialState() async throws {
        await MainActor.run {
            let vm = makeGmailViewModel()

            #expect(vm.emails.isEmpty)
            #expect(vm.selectedEmail == nil)
            #expect(vm.isLoading == false)
            #expect(vm.searchText.isEmpty)
            #expect(vm.error == nil)
            #expect(vm.sendSuccess == false)
            #expect(vm.isSending == false)
        }
    }

    @Test func filteredEmailsReturnsAllWhenSearchEmpty() async throws {
        await MainActor.run {
            let vm = makeGmailViewModel()
            vm.emails = [
                GmailMessageSummary(id: "1", snippet: "Hello", subject: "Meeting", from: "alice@test.com", date: "2025-06-15"),
                GmailMessageSummary(id: "2", snippet: "Update", subject: "Report", from: "bob@test.com", date: "2025-06-14")
            ]
            vm.searchText = ""

            #expect(vm.filteredEmails.count == 2)
        }
    }

    @Test func filteredEmailsFiltersBySubject() async throws {
        await MainActor.run {
            let vm = makeGmailViewModel()
            vm.emails = [
                GmailMessageSummary(id: "1", snippet: "Hello", subject: "Meeting", from: "alice@test.com", date: "2025-06-15"),
                GmailMessageSummary(id: "2", snippet: "Update", subject: "Report", from: "bob@test.com", date: "2025-06-14")
            ]
            vm.searchText = "meeting"

            #expect(vm.filteredEmails.count == 1)
            #expect(vm.filteredEmails[0].id == "1")
        }
    }

    @Test func filteredEmailsFiltersByFrom() async throws {
        await MainActor.run {
            let vm = makeGmailViewModel()
            vm.emails = [
                GmailMessageSummary(id: "1", snippet: "Hello", subject: "Meeting", from: "alice@test.com", date: "2025-06-15"),
                GmailMessageSummary(id: "2", snippet: "Update", subject: "Report", from: "bob@test.com", date: "2025-06-14")
            ]
            vm.searchText = "bob"

            #expect(vm.filteredEmails.count == 1)
            #expect(vm.filteredEmails[0].id == "2")
        }
    }

    @Test func filteredEmailsFiltersBySnippet() async throws {
        await MainActor.run {
            let vm = makeGmailViewModel()
            vm.emails = [
                GmailMessageSummary(id: "1", snippet: "Hello there", subject: "Meeting", from: "alice@test.com", date: "2025-06-15"),
                GmailMessageSummary(id: "2", snippet: "Status update", subject: "Report", from: "bob@test.com", date: "2025-06-14")
            ]
            vm.searchText = "status"

            #expect(vm.filteredEmails.count == 1)
            #expect(vm.filteredEmails[0].id == "2")
        }
    }

    @Test func loadInboxCallsSearch() async throws {
        let mockSearch = MockSearchGmailUseCase()
        mockSearch.result = [
            GmailMessageSummary(id: "1", snippet: "Hello", subject: "Test", from: "a@t.com", date: "d")
        ]

        await MainActor.run {
            let vm = makeGmailViewModel(search: mockSearch)

            Task {
                await vm.loadInbox()
            }
        }
    }

    @Test func sendEmailSuccess() async throws {
        let mockSend = MockSendGmailMessageUseCase()
        mockSend.shouldThrow = false

        let vm = await MainActor.run {
            makeGmailViewModel(sendMessage: mockSend)
        }

        await vm.sendEmail(to: "user@test.com", subject: "Hi", body: "Body", cc: nil, bcc: nil)

        await MainActor.run {
            #expect(vm.sendSuccess == true)
            #expect(vm.isSending == false)
            #expect(vm.error == nil)
        }
    }

    @Test func sendEmailFailure() async throws {
        let mockSend = MockSendGmailMessageUseCase()
        mockSend.shouldThrow = true

        let vm = await MainActor.run {
            makeGmailViewModel(sendMessage: mockSend)
        }

        await vm.sendEmail(to: "user@test.com", subject: "Hi", body: "Body", cc: nil, bcc: nil)

        await MainActor.run {
            #expect(vm.sendSuccess == false)
            #expect(vm.isSending == false)
            #expect(vm.error != nil)
        }
    }
}

// MARK: - Scheduled Emails ViewModel Tests

private final class MockGetScheduledEmailsUseCase: GetScheduledEmailsUseCaseProtocol, @unchecked Sendable {
    var result: [ScheduledEmail] = []
    var shouldThrow = false

    func execute(status: String?) async throws -> [ScheduledEmail] {
        if shouldThrow { throw URLError(.badServerResponse) }
        return result
    }
}

private final class MockUpdateScheduledEmailUseCase: UpdateScheduledEmailUseCaseProtocol, @unchecked Sendable {
    var shouldThrow = false
    var updatedEmail: ScheduledEmail?

    func execute(id: String, to: String?, subject: String?, body: String?, scheduledAt: String?) async throws -> ScheduledEmail {
        if shouldThrow { throw URLError(.badServerResponse) }
        return updatedEmail ?? ScheduledEmail(id: id, to: to ?? "t", subject: subject ?? "s", body: body ?? "b", cc: nil, bcc: nil, scheduledAt: scheduledAt ?? "t", status: .active, createdAt: nil, lastRunAt: nil, runCount: 0)
    }
}

private final class MockDeleteScheduledEmailUseCase: DeleteScheduledEmailUseCaseProtocol, @unchecked Sendable {
    var shouldThrow = false

    func execute(id: String) async throws {
        if shouldThrow { throw URLError(.badServerResponse) }
    }
}

struct ScheduledEmailsViewModelTests {

    @MainActor
    private func makeVM(
        getEmails: MockGetScheduledEmailsUseCase = MockGetScheduledEmailsUseCase(),
        updateEmail: MockUpdateScheduledEmailUseCase = MockUpdateScheduledEmailUseCase(),
        deleteEmail: MockDeleteScheduledEmailUseCase = MockDeleteScheduledEmailUseCase()
    ) -> ScheduledEmailsViewModel {
        ScheduledEmailsViewModel(
            getScheduledEmailsUseCase: getEmails,
            updateScheduledEmailUseCase: updateEmail,
            deleteScheduledEmailUseCase: deleteEmail
        )
    }

    @Test func initialState() async throws {
        await MainActor.run {
            let vm = makeVM()

            #expect(vm.scheduledEmails.isEmpty)
            #expect(vm.isLoading == false)
            #expect(vm.selectedStatus == nil)
            #expect(vm.error == nil)
        }
    }

    @Test func computedCounts() async throws {
        await MainActor.run {
            let vm = makeVM()
            vm.scheduledEmails = [
                ScheduledEmail(id: "1", to: "a@t.com", subject: "S1", body: "B", cc: nil, bcc: nil, scheduledAt: "t", status: .active, createdAt: nil, lastRunAt: nil, runCount: 0),
                ScheduledEmail(id: "2", to: "b@t.com", subject: "S2", body: "B", cc: nil, bcc: nil, scheduledAt: "t", status: .active, createdAt: nil, lastRunAt: nil, runCount: 0),
                ScheduledEmail(id: "3", to: "c@t.com", subject: "S3", body: "B", cc: nil, bcc: nil, scheduledAt: "t", status: .completed, createdAt: nil, lastRunAt: nil, runCount: 1),
                ScheduledEmail(id: "4", to: "d@t.com", subject: "S4", body: "B", cc: nil, bcc: nil, scheduledAt: "t", status: .cancelled, createdAt: nil, lastRunAt: nil, runCount: 0),
            ]

            #expect(vm.activeCount == 2)
            #expect(vm.completedCount == 1)
            #expect(vm.cancelledCount == 1)
        }
    }

    @Test func filteredEmailsNoFilter() async throws {
        await MainActor.run {
            let vm = makeVM()
            vm.scheduledEmails = [
                ScheduledEmail(id: "1", to: "a@t.com", subject: "S1", body: "B", cc: nil, bcc: nil, scheduledAt: "t", status: .active, createdAt: nil, lastRunAt: nil, runCount: 0),
                ScheduledEmail(id: "2", to: "b@t.com", subject: "S2", body: "B", cc: nil, bcc: nil, scheduledAt: "t", status: .completed, createdAt: nil, lastRunAt: nil, runCount: 1),
            ]
            vm.selectedStatus = nil

            #expect(vm.filteredEmails.count == 2)
        }
    }

    @Test func filteredEmailsWithStatusFilter() async throws {
        await MainActor.run {
            let vm = makeVM()
            vm.scheduledEmails = [
                ScheduledEmail(id: "1", to: "a@t.com", subject: "S1", body: "B", cc: nil, bcc: nil, scheduledAt: "t", status: .active, createdAt: nil, lastRunAt: nil, runCount: 0),
                ScheduledEmail(id: "2", to: "b@t.com", subject: "S2", body: "B", cc: nil, bcc: nil, scheduledAt: "t", status: .completed, createdAt: nil, lastRunAt: nil, runCount: 1),
                ScheduledEmail(id: "3", to: "c@t.com", subject: "S3", body: "B", cc: nil, bcc: nil, scheduledAt: "t", status: .active, createdAt: nil, lastRunAt: nil, runCount: 0),
            ]
            vm.selectedStatus = .active

            #expect(vm.filteredEmails.count == 2)
            #expect(vm.filteredEmails.allSatisfy { $0.status == .active })
        }
    }

    @Test func loadEmailsSuccess() async throws {
        let mockGet = MockGetScheduledEmailsUseCase()
        mockGet.result = [
            ScheduledEmail(id: "1", to: "a@t.com", subject: "S1", body: "B", cc: nil, bcc: nil, scheduledAt: "t", status: .active, createdAt: nil, lastRunAt: nil, runCount: 0)
        ]

        let vm = await MainActor.run { makeVM(getEmails: mockGet) }
        await vm.loadEmails()

        await MainActor.run {
            #expect(vm.scheduledEmails.count == 1)
            #expect(vm.isLoading == false)
            #expect(vm.error == nil)
        }
    }

    @Test func loadEmailsFailure() async throws {
        let mockGet = MockGetScheduledEmailsUseCase()
        mockGet.shouldThrow = true

        let vm = await MainActor.run { makeVM(getEmails: mockGet) }
        await vm.loadEmails()

        await MainActor.run {
            #expect(vm.scheduledEmails.isEmpty)
            #expect(vm.isLoading == false)
            #expect(vm.error != nil)
        }
    }

    @Test func cancelEmailSuccess() async throws {
        let mockDelete = MockDeleteScheduledEmailUseCase()
        mockDelete.shouldThrow = false

        let vm = await MainActor.run {
            let v = makeVM(deleteEmail: mockDelete)
            v.scheduledEmails = [
                ScheduledEmail(id: "1", to: "a@t.com", subject: "S", body: "B", cc: nil, bcc: nil, scheduledAt: "t", status: .active, createdAt: nil, lastRunAt: nil, runCount: 0),
                ScheduledEmail(id: "2", to: "b@t.com", subject: "S2", body: "B", cc: nil, bcc: nil, scheduledAt: "t", status: .active, createdAt: nil, lastRunAt: nil, runCount: 0),
            ]
            return v
        }

        await vm.cancelEmail(id: "1")

        await MainActor.run {
            #expect(vm.scheduledEmails.count == 1)
            #expect(vm.scheduledEmails[0].id == "2")
            #expect(vm.error == nil)
        }
    }

    @Test func cancelEmailFailure() async throws {
        let mockDelete = MockDeleteScheduledEmailUseCase()
        mockDelete.shouldThrow = true

        let vm = await MainActor.run {
            let v = makeVM(deleteEmail: mockDelete)
            v.scheduledEmails = [
                ScheduledEmail(id: "1", to: "a@t.com", subject: "S", body: "B", cc: nil, bcc: nil, scheduledAt: "t", status: .active, createdAt: nil, lastRunAt: nil, runCount: 0)
            ]
            return v
        }

        await vm.cancelEmail(id: "1")

        await MainActor.run {
            // Email should still be there since delete failed
            #expect(vm.scheduledEmails.count == 1)
            #expect(vm.error != nil)
        }
    }

    @Test func updateEmailSuccess() async throws {
        let mockUpdate = MockUpdateScheduledEmailUseCase()
        let updatedEmail = ScheduledEmail(id: "1", to: "new@t.com", subject: "Updated", body: "B", cc: nil, bcc: nil, scheduledAt: "t", status: .active, createdAt: nil, lastRunAt: nil, runCount: 0)
        mockUpdate.updatedEmail = updatedEmail

        let vm = await MainActor.run {
            let v = makeVM(updateEmail: mockUpdate)
            v.scheduledEmails = [
                ScheduledEmail(id: "1", to: "old@t.com", subject: "Original", body: "B", cc: nil, bcc: nil, scheduledAt: "t", status: .active, createdAt: nil, lastRunAt: nil, runCount: 0)
            ]
            return v
        }

        await vm.updateEmail(id: "1", to: "new@t.com", subject: "Updated")

        await MainActor.run {
            #expect(vm.scheduledEmails[0].to == "new@t.com")
            #expect(vm.scheduledEmails[0].subject == "Updated")
            #expect(vm.error == nil)
        }
    }
}
