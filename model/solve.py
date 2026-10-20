"""Solve-fors, discount-rate scenarios and sensitivities.

These replace the Goal Seek and data-table steps in the Excel answer key.
Tariffs are returned in US cents/kWh and LCOE in US cents/kWh, as in Excel's
Outputs sheet. Rates are fractions.
"""

from dataclasses import replace

import pandas as pd
from scipy.optimize import brentq

from model.engine import run_model
from model.inputs import load_inputs, load_range

# Tariff search range for the solve-fors, in USD/kWh (0.1 to 20 US cents/kWh).
TARIFF_RANGE = (0.001, 0.20)
# Discount-rate search range for the implied discount rate.
DISCOUNT_RATE_RANGE = (-0.5, 1.0)

# Tornado drivers, in the order of the answer key's sensitivity table.
SENSITIVITY_DRIVERS = {
    "Capex": "capex",
    "Discount rate": "discount_rate",
    "Specific yield": "specific_yield_year1",
    "Debt rate": "debt_rate",
    "Fixed O&M": "fixed_om",
    "Gearing": "gearing",
    "Degradation": "degradation",
    "DC/AC ratio": "dc_ac_ratio",
}


def _solve(function, low: float, high: float, what: str) -> float:
    if (function(low) > 0) == (function(high) > 0):
        raise ValueError(f"No solution for {what} between {low} and {high}")
    return brentq(function, low, high, xtol=1e-12, maxiter=500)


def tariff_for_equity_irr(country: str, target: float | None = None) -> float:
    """PPA tariff (US cents/kWh) at which equity IRR equals the target."""
    inputs = load_inputs(country)
    target = inputs.target_equity_irr if target is None else target

    def gap(tariff):
        results = run_model(replace(inputs, ppa_tariff=tariff))
        equity_irr = results.equity_irr
        if equity_irr is None:
            # Outside the IRR search range: below -99% if equity never gets
            # its money back, above +100% if it does.
            money_back = results.table["equity_cash_flow"].sum() > 0
            equity_irr = 1.0 if money_back else -1.0
        return equity_irr - target

    return _solve(gap, *TARIFF_RANGE, "tariff for target equity IRR") * 100


def tariff_for_min_dscr(country: str, target: float | None = None) -> float:
    """PPA tariff (US cents/kWh) at which the minimum DSCR equals the target."""
    inputs = load_inputs(country)
    target = inputs.target_min_dscr if target is None else target

    def gap(tariff):
        return run_model(replace(inputs, ppa_tariff=tariff)).min_dscr - target

    return _solve(gap, *TARIFF_RANGE, "tariff for target minimum DSCR") * 100


def implied_discount_rate(country: str) -> float:
    """Discount rate at which LCOE equals the PPA tariff."""
    inputs = load_inputs(country)
    tariff_cents = inputs.ppa_tariff * 100

    def gap(rate):
        return run_model(replace(inputs, discount_rate=rate)).lcoe_cents_per_kwh - tariff_cents

    return _solve(gap, *DISCOUNT_RATE_RANGE, "implied discount rate")


def discount_scenarios(country: str) -> dict[str, float]:
    """LCOE (US cents/kWh) at the base discount rate and the two premium scenarios."""
    inputs = load_inputs(country)
    rates = {
        "base": inputs.discount_rate,
        "conflict": inputs.discount_rate + inputs.conflict_premium,
        "severe": inputs.discount_rate + inputs.severe_premium,
    }
    return {
        name: run_model(replace(inputs, discount_rate=rate)).lcoe_cents_per_kwh
        for name, rate in rates.items()
    }


def sensitivities(country: str) -> pd.DataFrame:
    """LCOE and equity IRR with each driver at its low and high value from the CSV."""
    inputs = load_inputs(country)
    rows = []
    for driver, parameter in SENSITIVITY_DRIVERS.items():
        low, high = load_range(country, parameter)
        low_case = run_model(replace(inputs, **{parameter: low}))
        high_case = run_model(replace(inputs, **{parameter: high}))
        rows.append(
            {
                "driver": driver,
                "parameter": parameter,
                "low_input": low,
                "high_input": high,
                "lcoe_low": low_case.lcoe_cents_per_kwh,
                "lcoe_high": high_case.lcoe_cents_per_kwh,
                "equity_irr_low": low_case.equity_irr,
                "equity_irr_high": high_case.equity_irr,
            }
        )
    return pd.DataFrame(rows).set_index("driver")
