import Foundation

/// Mapper for ScheduledEmail DTOs
enum ScheduledEmailMapper {
    static func toDomain(_ dto: ScheduledEmailDTO) -> ScheduledEmail {
        ScheduledEmail(
            id: dto.id,
            to: dto.to,
            subject: dto.subject,
            body: dto.body,
            cc: dto.cc,
            bcc: dto.bcc,
            scheduledAt: dto.scheduledAt,
            status: ScheduledEmailStatus(rawValue: dto.status) ?? .active,
            createdAt: dto.createdAt,
            lastRunAt: dto.lastRunAt,
            runCount: dto.runCount ?? 0
        )
    }
}
