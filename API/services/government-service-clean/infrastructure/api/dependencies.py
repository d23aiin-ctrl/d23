"""Dependency Injection."""
from functools import lru_cache
from domain.repositories import PMKisanRepository, DLRepository, VehicleRepository, EChallanRepository
from infrastructure.repositories import MockPMKisanRepository, MockDLRepository, MockVehicleRepository, MockEChallanRepository
from application.use_cases import GetPMKisanStatusUseCase, GetDLStatusUseCase, GetVehicleRCUseCase, GetEChallansUseCase

@lru_cache()
def get_pmkisan_repository() -> PMKisanRepository:
    return MockPMKisanRepository()

@lru_cache()
def get_dl_repository() -> DLRepository:
    return MockDLRepository()

@lru_cache()
def get_vehicle_repository() -> VehicleRepository:
    return MockVehicleRepository()

@lru_cache()
def get_echallan_repository() -> EChallanRepository:
    return MockEChallanRepository()

def get_pmkisan_use_case() -> GetPMKisanStatusUseCase:
    return GetPMKisanStatusUseCase(pmkisan_repository=get_pmkisan_repository())

def get_dl_use_case() -> GetDLStatusUseCase:
    return GetDLStatusUseCase(dl_repository=get_dl_repository())

def get_vehicle_use_case() -> GetVehicleRCUseCase:
    return GetVehicleRCUseCase(vehicle_repository=get_vehicle_repository())

def get_echallan_use_case() -> GetEChallansUseCase:
    return GetEChallansUseCase(echallan_repository=get_echallan_repository())
