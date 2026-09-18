from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.twin_profile import TwinProfile
from app.schemas.simulation import (
    SimulationRequest,
    SimulationResponse,
)

from app.simulation.engine import (
    FinancialProfile,
    LoanScenario,
    simulate_baseline,
    simulate_loan,
    compare_results,
)

from app.simulation.monte_carlo import (
    monte_carlo_baseline,
    monte_carlo_loan,
)


router = APIRouter(
    prefix="/simulate",
    tags=["Simulation"],
)

DEMO_PROFILE_ID = 1


@router.post(
    "",
    response_model=SimulationResponse,
    summary="Run financial simulation",
)
def run_simulation(
    request: SimulationRequest,
    database: Session = Depends(get_db),
):
    # Get profile from database
    profile_data = database.get(
        TwinProfile,
        DEMO_PROFILE_ID,
    )

    if profile_data is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Financial profile has not been created",
        )

    # Convert database profile to simulation profile
    profile = FinancialProfile(
        monthly_income=profile_data.monthly_income,
        monthly_expenses=profile_data.monthly_expenses,
        savings=profile_data.cash_savings,
        investments=profile_data.investments,
        monthly_investment=profile_data.monthly_investment,
        existing_debt=profile_data.existing_debt,
    )

    # Baseline simulation
    baseline = simulate_baseline(
        profile=profile,
        months=request.months,
        annual_investment_return=request.annual_investment_return,
        annual_inflation=request.annual_inflation,
    )

    scenario = None
    comparison = None
    monte_carlo = None
    loan = None

    # Loan scenario
    if request.type == "loan":

        if request.loan is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Loan details are required for a loan simulation",
            )

        loan = LoanScenario(
            amount=request.loan.amount,
            interest_rate=request.loan.interest_rate,
            duration_months=request.loan.duration_months,
        )

        scenario = simulate_loan(
            profile=profile,
            scenario=loan,
            months=request.months,
            annual_investment_return=request.annual_investment_return,
            annual_inflation=request.annual_inflation,
        )

        comparison = compare_results(
            baseline,
            scenario,
        )

    # Monte Carlo
    if request.monte_carlo:

        if request.type == "baseline":

            monte_carlo = monte_carlo_baseline(
                profile=profile,
                months=request.months,
                simulations=request.simulations,
            )

        else:

            monte_carlo = monte_carlo_loan(
                profile=profile,
                scenario=loan,
                months=request.months,
                simulations=request.simulations,
            )

    return SimulationResponse(
        baseline=baseline,
        scenario=scenario,
        comparison=comparison,
        monte_carlo=monte_carlo,
    )