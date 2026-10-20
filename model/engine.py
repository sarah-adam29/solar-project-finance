"""The calculation engine: inputs in, annual cash flows and metrics out.

It follows the Excel answer key (excel/solar_answer_key.xlsx) line by line:
annual periods, period 1 = financial close, construction years first, then
operating years up to the PPA term. All flows are at year end and are valued
at financial close.
"""

from dataclasses import dataclass

import numpy as np
import pandas as pd
from scipy.optimize import brentq

from model.inputs import Inputs

HOURS_PER_YEAR = 8760


@dataclass(frozen=True)
class Results:
    """The annual table plus the headline metrics.

    Money is in USD, generation in MWh, rates and IRRs as fractions.
    An IRR is None when its cash flow never changes sign.
    """

    table: pd.DataFrame  # one row per period

    lcoe_usd_per_mwh: float
    lcoe_cents_per_kwh: float
    project_irr: float | None
    equity_irr: float | None
    project_npv: float
    min_dscr: float
    average_dscr: float

    total_capex: float
    capitalised_interest: float
    debt_at_cod: float
    equity: float
    effective_gearing_at_cod: float
    annuity_payment: float

    year1_generation_mwh: float
    capacity_factor: float


def irr(cash_flows) -> float | None:
    """Internal rate of return, with the first cash flow at time 0 (as Excel's IRR).

    Searches between -99% and +100% with a bracketed solver, so it does not
    depend on a starting guess. Returns None if NPV has no sign change there.
    """
    cash_flows = np.asarray(cash_flows, dtype=float)
    years = np.arange(len(cash_flows))

    def npv(rate):
        return float(np.sum(cash_flows / (1 + rate) ** years))

    low, high = -0.99, 1.0
    if np.sign(npv(low)) == np.sign(npv(high)):
        return None
    return brentq(npv, low, high, xtol=1e-12, maxiter=500)


def annuity_payment(debt: float, rate: float, years: int) -> float:
    """Level annual payment that repays `debt` over `years` (Excel's PMT)."""
    if rate == 0:
        return debt / years
    return debt * rate / (1 - (1 + rate) ** -years)


def _tax(inputs: Inputs, taxable_income: np.ndarray) -> np.ndarray:
    """Tax for one year's taxable income. No loss carry-forward in v1."""
    if inputs.country == "KSA":
        # Income tax on the foreign-owned share, zakat on the Saudi/GCC share.
        foreign = inputs.foreign_ownership_share
        rate = foreign * inputs.corporate_income_tax + (1 - foreign) * inputs.zakat
        return np.maximum(taxable_income, 0) * rate
    if inputs.country == "UAE":
        # 9% on taxable income above AED 375,000, converted to USD at the peg.
        threshold_usd = inputs.uae_tax_threshold / inputs.aed_per_usd
        return np.maximum(taxable_income - threshold_usd, 0) * inputs.corporate_tax
    raise ValueError(f"No tax rules for country {inputs.country!r}")


def _check(inputs: Inputs) -> None:
    if inputs.construction_years != 2:
        raise ValueError("v1 supports a 2-year construction period only")
    if abs(inputs.capex_phase_y1 + inputs.capex_phase_y2 - 1) > 1e-9:
        raise ValueError("Capex phasing must add up to 100%")
    if inputs.debt_tenor > inputs.ppa_term:
        raise ValueError("Debt tenor cannot be longer than the PPA term")


def run_model(inputs: Inputs) -> Results:
    _check(inputs)
    rate = inputs.debt_rate

    # --- Timeline --------------------------------------------------------
    construction_years = inputs.construction_years
    periods = construction_years + inputs.ppa_term
    period = np.arange(1, periods + 1)
    construction = period <= construction_years
    operating = ~construction
    operating_year = np.where(operating, period - construction_years, 0)
    repayment = operating & (operating_year <= inputs.debt_tenor)
    discount_factor = 1 / (1 + inputs.discount_rate) ** period

    # --- Construction funding --------------------------------------------
    total_capex = inputs.capex * inputs.capacity * 1000
    capex_spend = np.zeros(periods)
    capex_spend[:construction_years] = total_capex * np.array(
        [inputs.capex_phase_y1, inputs.capex_phase_y2]
    )
    debt_drawdown = capex_spend * inputs.gearing
    equity_contribution = capex_spend - debt_drawdown

    # Interest during construction: everything drawn in earlier years
    # (including interest already capitalised) x debt rate. It is worked out
    # here, outside the loan account, so debt sizing is not circular.
    capitalised_interest = np.zeros(periods)
    drawn_so_far = 0.0
    for i in range(construction_years):
        capitalised_interest[i] = drawn_so_far * rate
        drawn_so_far += debt_drawdown[i] + capitalised_interest[i]
    debt_at_cod = drawn_so_far

    # Annuity worked out once, on debt at COD.
    annuity = annuity_payment(debt_at_cod, rate, inputs.debt_tenor)
    debt_service = np.where(repayment, annuity, 0.0)

    # --- Loan account ----------------------------------------------------
    opening_balance = np.zeros(periods)
    interest_paid = np.zeros(periods)
    principal_repaid = np.zeros(periods)
    closing_balance = np.zeros(periods)
    balance = 0.0
    for i in range(periods):
        opening_balance[i] = balance
        interest_paid[i] = balance * rate if operating[i] else 0.0
        principal_repaid[i] = debt_service[i] - interest_paid[i]
        balance = balance + debt_drawdown[i] + capitalised_interest[i] - principal_repaid[i]
        closing_balance[i] = balance

    # --- Operations ------------------------------------------------------
    dc_capacity_mwp = inputs.capacity * inputs.dc_ac_ratio
    year1_generation = dc_capacity_mwp * inputs.specific_yield_year1  # MWh
    generation = np.where(
        operating, year1_generation * (1 - inputs.degradation) ** (operating_year - 1), 0.0
    )
    revenue = generation * inputs.ppa_tariff * 1000  # USD/kWh -> USD/MWh
    om_cost = np.where(operating, inputs.capacity * 1000 * inputs.fixed_om, 0.0)
    ebitda = revenue - om_cost

    # --- Tax -------------------------------------------------------------
    depreciable_base = total_capex + capitalised_interest.sum()
    depreciation = np.where(operating, depreciable_base / inputs.project_life, 0.0)
    taxable_income = ebitda - interest_paid - depreciation
    tax = np.where(operating, _tax(inputs, taxable_income), 0.0)
    unlevered_taxable_income = ebitda - depreciation
    unlevered_tax = np.where(operating, _tax(inputs, unlevered_taxable_income), 0.0)

    # --- Cash flows ------------------------------------------------------
    cfads = ebitda - tax
    dscr = np.full(periods, np.nan)
    dscr[repayment] = cfads[repayment] / debt_service[repayment]
    equity_cash_flow = -equity_contribution + cfads - debt_service
    project_cash_flow = -capex_spend + ebitda - unlevered_tax

    table = pd.DataFrame(
        {
            "period": period,
            "construction": construction,
            "operating": operating,
            "operating_year": operating_year,
            "repayment": repayment,
            "discount_factor": discount_factor,
            "capex_spend": capex_spend,
            "debt_drawdown": debt_drawdown,
            "equity_contribution": equity_contribution,
            "capitalised_interest": capitalised_interest,
            "opening_balance": opening_balance,
            "debt_service": debt_service,
            "interest_paid": interest_paid,
            "principal_repaid": principal_repaid,
            "closing_balance": closing_balance,
            "generation_mwh": generation,
            "revenue": revenue,
            "om_cost": om_cost,
            "ebitda": ebitda,
            "depreciation": depreciation,
            "taxable_income": taxable_income,
            "tax": tax,
            "unlevered_taxable_income": unlevered_taxable_income,
            "unlevered_tax": unlevered_tax,
            "cfads": cfads,
            "dscr": dscr,
            "equity_cash_flow": equity_cash_flow,
            "project_cash_flow": project_cash_flow,
        }
    ).set_index("period")

    # --- Metrics ---------------------------------------------------------
    lcoe = (np.sum(capex_spend * discount_factor) + np.sum(om_cost * discount_factor)) / np.sum(
        generation * discount_factor
    )
    capitalised_total = capitalised_interest.sum()

    return Results(
        table=table,
        lcoe_usd_per_mwh=lcoe,
        lcoe_cents_per_kwh=lcoe / 10,
        project_irr=irr(project_cash_flow),
        equity_irr=irr(equity_cash_flow),
        # Same timing as Excel's NPV(): period 1 is discounted once.
        project_npv=float(np.sum(project_cash_flow * discount_factor)),
        min_dscr=float(np.min(dscr[repayment])),
        average_dscr=float(np.mean(dscr[repayment])),
        total_capex=total_capex,
        capitalised_interest=capitalised_total,
        debt_at_cod=debt_at_cod,
        equity=equity_contribution.sum(),
        effective_gearing_at_cod=debt_at_cod / (total_capex + capitalised_total),
        annuity_payment=annuity,
        year1_generation_mwh=year1_generation,
        capacity_factor=year1_generation / (inputs.capacity * HOURS_PER_YEAR),
    )
