import Foundation

/// DTO for Gmail search results
struct GmailSearchResponseDTO: Decodable {
    let emails: [GmailMessageSummaryDTO]
}

/// DTO for Gmail message summary
struct GmailMessageSummaryDTO: Decodable {
    let id: String
    let snippet: String?
    let subject: String?
    let from: String?
    let date: String?
}

/// DTO for Gmail message detail
struct GmailMessageDetailDTO: Decodable {
    let id: String
    let threadId: String?
    let snippet: String?
    let subject: String?
    let from: String?
    let to: String?
    let cc: String?
    let date: String?
    let body: String?
    let labelIds: [String]?
}

/// DTO for Gmail send request
struct GmailSendRequestDTO: Encodable {
    let to: String
    let subject: String
    let body: String
    let cc: String?
    let bcc: String?
    let html: Bool
}

/// DTO for Gmail send response
struct GmailSendResponseDTO: Decodable {
    let success: Bool
    let messageId: String?
    let threadId: String?

    enum CodingKeys: String, CodingKey {
        case success
        case messageId = "message_id"
        case threadId = "thread_id"
    }
}
