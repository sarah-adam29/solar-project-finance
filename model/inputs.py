"""Load model inputs from data/assumptions.csv.

The CSV stores inputs in the units people quote them in (72 %, 1.30 US cents/kWh,
70 bp). The model works in plain units (0.72, 0.013 USD/kWh, 0.007), so every
value is converted here, once, on the way in.
"""

from dataclasses import dataclass, fields, replace
from pathlib import Path

import pandas as pd

ASSUMPTIONS_CSV = Path(__file__).resolve().parent.parent / "data" / "assumptions.csv"

COUNTRIES = ("KSA", "UAE")

# Tax inputs that exist for one country only. The other country leaves them as None.
KSA_ONLY = ("corporate_income_tax", "zakat", "foreign_ownership_share")
UAE_ONLY = ("corporate_tax", "uae_tax_threshold", "aed_per_usd")


@dataclass(frozen=True)
class Inputs:
    """Every model input, in model units: fractions (not %), USD (not cents)."""

    country: str

    # Plant
    capacity: float  # MWac
    dc_ac_ratio: float  # MWp per MWac
    specific_yield_year1: float  # kWh per kWp in the first operating year
    degradation: float  # fraction per year

    # Construction
    construction_years: int
    capex_phase_y1: float  # fraction of capex spent in construction year 1
    capex_phase_y2: float  # fraction of capex spent in construction year 2

    # Costs
    capex: float  # USD per kWac
    fixed_om: float  # USD per kWac per year

    # Revenue
    ppa_tariff: float  # USD per kWh
    ppa_term: int  # operating years

    # Financing
    gearing: float  # debt share of capex
    debt_tenor: int  # repayment years from COD
    debt_rate: float  # all-in annual rate

    # Valuation and targets
    discount_rate: float  # nominal, after tax
    project_life: int  # years; depreciation period
    target_equity_irr: float
    target_min_dscr: float  # x
    conflict_premium: float  # added to the discount rate
    severe_premium: float  # added to the discount rate

    # Tax: KSA only
    corporate_income_tax: float | None = None  # on the foreign-owned share of profit
    zakat: float | None = None  # on the Saudi/GCC share (v1: applied to profit)
    foreign_ownership_share: float | None = None

    # Tax: UAE only
    corporate_tax: float | None = None  # on taxable income above the threshold
    uae_tax_threshold: float | None = None  # AED
    aed_per_usd: float | None = None


# How to turn each CSV unit into a model unit.
UNIT_FACTORS = {
    "%": 0.01,
    "%/yr": 0.01,
    "% debt": 0.01,
    "% all-in": 0.01,
    "% of zakat base": 0.01,
    "% nominal after tax": 0.01,
    "% of capex": 0.01,
    "USc/kWh": 0.01,  # US cents to USD
    "bp": 0.0001,
}

INTEGER_FIELDS = {"construction_years", "ppa_term", "debt_tenor", "project_life"}


def _to_model_units(value: float, unit: str, parameter: str) -> float | int:
    value = value * UNIT_FACTORS.get(unit, 1.0)
    if parameter in INTEGER_FIELDS:
        return int(round(value))
    return value


def _country_rows(country: str) -> pd.DataFrame:
    if country not in COUNTRIES:
        raise ValueError(f"country must be one of {COUNTRIES}, not {country!r}")
    table = pd.read_csv(ASSUMPTIONS_CSV)
    rows = table[table["country"] == country]
    duplicates = rows["parameter"][rows["parameter"].duplicated()]
    if not duplicates.empty:
        raise ValueError(f"Duplicate {country} rows in assumptions.csv: {list(duplicates)}")
    return rows.set_index("parameter")


def load_inputs(country: str, overrides: dict | None = None) -> Inputs:
    """Read one country's base inputs from the CSV, in model units.

    `overrides` replaces fields after loading, e.g. {"capex": 450}. Values in
    `overrides` must already be in model units (fractions, USD).
    """
    rows = _country_rows(country)
    other_country_fields = UAE_ONLY if country == "KSA" else KSA_ONLY

    values = {"country": country}
    for field in fields(Inputs):
        name = field.name
        if name == "country" or name in other_country_fields:
            continue
        if name not in rows.index:
            raise ValueError(f"assumptions.csv has no {country} row for {name!r}")
        row = rows.loc[name]
        values[name] = _to_model_units(float(row["base"]), row["unit"], name)

    inputs = Inputs(**values)
    if overrides:
        unknown = set(overrides) - {f.name for f in fields(Inputs)}
        if unknown:
            raise ValueError(f"Unknown input(s) in overrides: {sorted(unknown)}")
        inputs = replace(inputs, **overrides)

    # v1 depreciates over project life and operates for the PPA term, so the two must match.
    if inputs.project_life != inputs.ppa_term:
        raise ValueError(
            f"{country}: project_life ({inputs.project_life}) must equal ppa_term "
            f"({inputs.ppa_term}) in v1. Change both together."
        )
    return inputs


def load_range(country: str, parameter: str) -> tuple[float, float]:
    """Low and high values for one input from the CSV, in model units."""
    row = _country_rows(country).loc[parameter]
    if pd.isna(row["low"]) or pd.isna(row["high"]):
        raise ValueError(f"assumptions.csv has no low/high for {country} {parameter!r}")
    return (
        _to_model_units(float(row["low"]), row["unit"], parameter),
        _to_model_units(float(row["high"]), row["unit"], parameter),
    )
