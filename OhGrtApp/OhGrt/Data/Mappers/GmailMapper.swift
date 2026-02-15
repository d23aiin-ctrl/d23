import Foundation

/// Mapper for Gmail DTOs
enum GmailMapper {
    static func toDomain(_ dto: GmailMessageSummaryDTO) -> GmailMessageSummary {
        GmailMessageSummary(
            id: dto.id,
            snippet: dto.snippet ?? "",
            subject: dto.subject ?? "(No subject)",
            from: dto.from ?? "",
            date: dto.date ?? ""
        )
    }

    static func toDomain(_ dto: GmailMessageDetailDTO) -> GmailMessageDetail {
        GmailMessageDetail(
            id: dto.id,
            threadId: dto.threadId,
            snippet: dto.snippet ?? "",
            subject: dto.subject ?? "(No subject)",
            from: dto.from ?? "",
            to: dto.to ?? "",
            cc: dto.cc,
            date: dto.date ?? "",
            body: dto.body ?? "",
            labelIds: dto.labelIds ?? []
        )
    }
}
