"""Get Currency Rate Use Case."""
from domain.repositories import CurrencyRepository
from application.dto import CurrencyRequest, CurrencyResponse
from application.dto.currency_dto import CurrencyRateDTO, ConversionRequest, ConversionResponse


class CurrencyNotFoundError(Exception):
    """Raised when currency rate is not available."""
    pass


class GetCurrencyRateUseCase:
    """Use case for getting currency rates."""

    def __init__(self, currency_repository: CurrencyRepository):
        self.currency_repository = currency_repository

    async def execute(self, request: CurrencyRequest) -> CurrencyResponse:
        """Get currency rate."""
        rate = await self.currency_repository.get_rate(request.base, request.quote)

        if not rate:
            raise CurrencyNotFoundError(f"Rate not available for {request.base}/{request.quote}")

        return CurrencyResponse(
            success=True,
            data=CurrencyRateDTO(
                base=rate.pair.base,
                quote=rate.pair.quote,
                rate=rate.rate,
                change=rate.change,
                change_percent=rate.change_percent
            )
        )

    async def convert(self, request: ConversionRequest) -> ConversionResponse:
        """Convert currency amount."""
        rate = await self.currency_repository.get_rate(request.from_currency, request.to_currency)

        if not rate:
            raise CurrencyNotFoundError(f"Rate not available for {request.from_currency}/{request.to_currency}")

        converted = request.amount * rate.rate

        return ConversionResponse(
            success=True,
            amount=request.amount,
            from_currency=request.from_currency,
            to_currency=request.to_currency,
            converted_amount=round(converted, 2),
            rate=rate.rate
        )
