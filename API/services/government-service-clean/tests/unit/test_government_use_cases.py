"""Unit tests for Government Service use cases."""
import pytest
from application.use_cases import GetPMKisanStatusUseCase, GetDLStatusUseCase, GetVehicleRCUseCase, GetEChallansUseCase
from application.use_cases.get_pmkisan_status import PMKisanValidationError, PMKisanNotFoundError
from application.use_cases.get_dl_status import DLValidationError, DLNotFoundError
from application.use_cases.get_vehicle_rc import VehicleValidationError, VehicleNotFoundError
from application.dto import PMKisanRequest, DLRequest, EChallanRequest
from infrastructure.repositories import MockPMKisanRepository, MockDLRepository, MockVehicleRepository, MockEChallanRepository

class TestPMKisanUseCase:
    @pytest.fixture
    def use_case(self):
        return GetPMKisanStatusUseCase(pmkisan_repository=MockPMKisanRepository())

    @pytest.mark.asyncio
    async def test_get_by_mobile_success(self, use_case):
        request = PMKisanRequest(mobile="9876543210")
        result = await use_case.execute(request)
        assert result.success
        assert result.name == "Ramesh Kumar"
        assert result.total_received == 8000

    @pytest.mark.asyncio
    async def test_missing_identifier(self, use_case):
        request = PMKisanRequest()
        with pytest.raises(PMKisanValidationError):
            await use_case.execute(request)

    @pytest.mark.asyncio
    async def test_not_found(self, use_case):
        request = PMKisanRequest(mobile="1111111111")
        with pytest.raises(PMKisanNotFoundError):
            await use_case.execute(request)

class TestDLUseCase:
    @pytest.fixture
    def use_case(self):
        return GetDLStatusUseCase(dl_repository=MockDLRepository())

    @pytest.mark.asyncio
    async def test_get_dl_success(self, use_case):
        request = DLRequest(dl_number="DL0120160001234")
        result = await use_case.execute(request)
        assert result.success
        assert result.name == "Amit Sharma"
        assert result.is_valid

    @pytest.mark.asyncio
    async def test_invalid_dl_number(self, use_case):
        request = DLRequest(dl_number="short")
        with pytest.raises(DLValidationError):
            await use_case.execute(request)

class TestVehicleUseCase:
    @pytest.fixture
    def use_case(self):
        return GetVehicleRCUseCase(vehicle_repository=MockVehicleRepository())

    @pytest.mark.asyncio
    async def test_get_vehicle_success(self, use_case):
        result = await use_case.execute("DL01AB1234")
        assert result.success
        assert result.make == "Maruti Suzuki"
        assert result.model == "Swift VXI"

    @pytest.mark.asyncio
    async def test_vehicle_not_found(self, use_case):
        with pytest.raises(VehicleNotFoundError):
            await use_case.execute("XX00XX0000")

class TestEChallanUseCase:
    @pytest.fixture
    def use_case(self):
        return GetEChallansUseCase(echallan_repository=MockEChallanRepository())

    @pytest.mark.asyncio
    async def test_get_challans_success(self, use_case):
        request = EChallanRequest(vehicle_number="DL01AB1234")
        result = await use_case.execute(request)
        assert result.success
        assert result.total_challans == 2
        assert result.pending_challans == 1
