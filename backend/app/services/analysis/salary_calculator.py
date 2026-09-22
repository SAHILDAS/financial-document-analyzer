from decimal import Decimal

from app.schemas.salary_calculation import SalaryCalculationResult
from app.schemas.salary_slip import SalarySlip


class SalaryCalculator:
    """Perform deterministic calculations on extracted salary data."""

    def calculate(
        self,
        salary: SalarySlip,
    ) -> SalaryCalculationResult:
        earnings = salary.earnings

        earning_components = [
            earnings.basic,
            earnings.hra,
            earnings.allowances,
            earnings.bonus,
            earnings.other,
        ]

        can_calculate_earnings = all(
            value is not None
            for value in earning_components
        )

        calculated_earnings: Decimal | None = None

        if can_calculate_earnings:
            calculated_earnings = sum(
                earning_components,
                Decimal("0"),
            )

        reported_gross = earnings.gross

        earnings_difference: Decimal | None = None

        if (
            calculated_earnings is not None
            and reported_gross is not None
        ):
            earnings_difference = (
                calculated_earnings - reported_gross
            )

        deductions = salary.deductions.total
        reported_net = salary.net_salary

        can_calculate_net = (
            reported_gross is not None
            and deductions is not None
        )

        calculated_net: Decimal | None = None

        if can_calculate_net:
            calculated_net = reported_gross - deductions

        net_difference: Decimal | None = None

        if calculated_net is not None and reported_net is not None:
            net_difference = calculated_net - reported_net

        return SalaryCalculationResult(
            calculated_earnings=calculated_earnings,
            reported_gross=reported_gross,
            earnings_difference=earnings_difference,
            calculated_net=calculated_net,
            reported_net=reported_net,
            net_difference=net_difference,
            can_calculate_earnings=can_calculate_earnings,
            can_calculate_net=can_calculate_net,
        )