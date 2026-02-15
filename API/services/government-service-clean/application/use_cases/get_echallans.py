"""Get E-Challans Use Case."""
from dataclasses import dataclass
from domain.repositories import EChallanRepository
from application.dto import EChallanRequest, EChallanResponse, EChallanListResponse, ViolationDTO

class EChallanValidationError(Exception):
    pass

class EChallanNotFoundError(Exception):
    pass

@dataclass
class GetEChallansUseCase:
    echallan_repository: EChallanRepository

    async def execute(self, request: EChallanRequest) -> EChallanListResponse:
        if not request.vehicle_number and not request.challan_number:
            raise EChallanValidationError("Vehicle number or Challan number required")

        if request.challan_number:
            challan = await self.echallan_repository.get_by_challan_number(request.challan_number)
            if not challan:
                raise EChallanNotFoundError(f"Challan {request.challan_number} not found")
            challans = [challan]
            vehicle_number = challan.vehicle_number
        else:
            vehicle_number = request.vehicle_number.upper().replace(" ", "").replace("-", "")
            challans = await self.echallan_repository.get_by_vehicle(vehicle_number)

        challan_responses = []
        total_pending = 0

        for c in challans:
            violations = [
                ViolationDTO(
                    type=v.violation_type.description,
                    description=v.description or v.violation_type.description,
                    fine_amount=v.fine_amount
                )
                for v in c.violations
            ]

            if not c.is_paid:
                total_pending += c.total_fine

            challan_responses.append(EChallanResponse(
                challan_number=c.challan_number,
                challan_date=c.challan_date.strftime("%Y-%m-%d %H:%M"),
                vehicle_number=c.vehicle_number,
                location=c.location,
                city=c.city,
                state=c.state,
                violations=violations,
                total_fine=c.total_fine,
                status=c.status.value,
                is_paid=c.is_paid,
                is_overdue=c.is_overdue,
                due_date=c.due_date.strftime("%Y-%m-%d") if c.due_date else None,
                payment_date=c.payment_date.strftime("%Y-%m-%d") if c.payment_date else None
            ))

        pending_count = sum(1 for c in challans if not c.is_paid)

        return EChallanListResponse(
            vehicle_number=vehicle_number,
            total_challans=len(challans),
            pending_challans=pending_count,
            total_pending_amount=total_pending,
            challans=challan_responses
        )
