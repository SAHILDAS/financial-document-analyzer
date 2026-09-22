from decimal import Decimal

from pydantic import BaseModel


class SalaryCalculationResult(BaseModel):
    calculated_earnings: Decimal | None = None
    reported_gross: Decimal | None = None
    earnings_difference: Decimal | None = None

    calculated_net: Decimal | None = None
    reported_net: Decimal | None = None
    net_difference: Decimal | None = None

    can_calculate_earnings: bool
    can_calculate_net: bool