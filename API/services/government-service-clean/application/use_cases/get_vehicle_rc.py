"""Get Vehicle RC Use Case."""
from dataclasses import dataclass
from domain.repositories import VehicleRepository
from application.dto import VehicleRequest, VehicleResponse, OwnerDTO

class VehicleValidationError(Exception):
    pass

class VehicleNotFoundError(Exception):
    pass

@dataclass
class GetVehicleRCUseCase:
    vehicle_repository: VehicleRepository

    async def execute(self, registration_number: str) -> VehicleResponse:
        if not registration_number:
            raise VehicleValidationError("Registration number required")

        # Normalize vehicle number
        registration_number = registration_number.upper().replace(" ", "").replace("-", "")

        vehicle = await self.vehicle_repository.get_by_registration(registration_number)
        if not vehicle:
            raise VehicleNotFoundError(f"Vehicle {registration_number} not found")

        owner_dto = None
        if vehicle.owner:
            owner_dto = OwnerDTO(
                name=vehicle.owner.name,
                father_name=vehicle.owner.father_name,
                address=vehicle.owner.address
            )

        return VehicleResponse(
            registration_number=vehicle.registration_number,
            registration_date=vehicle.registration_date.strftime("%Y-%m-%d"),
            rto=f"{vehicle.rto_code} - {vehicle.rto_name}",
            state=vehicle.state,
            make=vehicle.make,
            model=vehicle.model,
            vehicle_type=vehicle.vehicle_type.value,
            fuel_type=vehicle.fuel_type.value,
            color=vehicle.color,
            engine_number=vehicle.engine_number,
            chassis_number=vehicle.chassis_number,
            cubic_capacity=vehicle.cubic_capacity,
            seating_capacity=vehicle.seating_capacity,
            owner=owner_dto,
            fitness_upto=vehicle.fitness_upto.strftime("%Y-%m-%d") if vehicle.fitness_upto else None,
            tax_upto=vehicle.tax_upto.strftime("%Y-%m-%d") if vehicle.tax_upto else None,
            insurance_upto=vehicle.insurance_upto.strftime("%Y-%m-%d") if vehicle.insurance_upto else None,
            pucc_upto=vehicle.pucc_upto.strftime("%Y-%m-%d") if vehicle.pucc_upto else None,
            is_financed=vehicle.is_financed,
            financer=vehicle.financer_name,
            is_blacklisted=vehicle.is_blacklisted,
            pending_documents=vehicle.pending_documents
        )
