import Foundation

/// DTO for scheduled email from API
struct ScheduledEmailDTO: Decodable {
    let id: String
    let to: String
    let subject: String
    let body: String
    let cc: String?
    let bcc: String?
    let scheduledAt: String
    let status: String
    let createdAt: String?
    let lastRunAt: String?
    let runCount: Int?

    enum CodingKeys: String, CodingKey {
        case id
        case to
        case subject
        case body
        case cc
        case bcc
        case scheduledAt = "scheduled_at"
        case status
        case createdAt = "created_at"
        case lastRunAt = "last_run_at"
        case runCount = "run_count"
    }
}

/// Request DTO for scheduling an email
struct ScheduleEmailRequestDTO: Encodable {
    let to: String
    let subject: String
    let body: String
    let cc: String?
    let bcc: String?
    let scheduledAt: String
    let timezone: String

    enum CodingKeys: String, CodingKey {
        case to
        case subject
        case body
        case cc
        case bcc
        case scheduledAt = "scheduled_at"
        case timezone
    }
}

/// Request DTO for updating a scheduled email
struct UpdateScheduledEmailRequestDTO: Encodable {
    let to: String?
    let subject: String?
    let body: String?
    let scheduledAt: String?

    enum CodingKeys: String, CodingKey {
        case to
        case subject
        case body
        case scheduledAt = "scheduled_at"
    }
}
