"""Check the Python engine against the Excel answer key.

Expected values are read straight from excel/solar_answer_key.xlsx (the values
Excel last calculated and saved). Nothing here is typed in by hand.

Pass rule: within 0.1% of the Excel value, or within 0.00001 for values close
to zero (some IRRs are near 0%).
"""

from functools import cache
from pathlib import Path

import openpyxl
import pytest

from model import solve
from model.engine import run_model
from model.inputs import load_inputs

ANSWER_KEY = Path(__file__).resolve().parent.parent / "excel" / "solar_answer_key.xlsx"
RELATIVE_TOLERANCE = 0.001
ABSOLUTE_TOLERANCE = 0.00001


@cache
def workbook():
    return openpyxl.load_workbook(ANSWER_KEY, data_only=True)


def excel(sheet: str, cell: str):
    return workbook()[sheet][cell].value


# --- Python values, each worked out once --------------------------------


@cache
def results(country):
    return run_model(load_inputs(country))


@cache
def sensitivities(country):
    return solve.sensitivities(country)


@cache
def tariff_cents(country):
    return load_inputs(country).ppa_tariff * 100


# --- Checks: (sheet, cell, description, Python value) -------------------

HEADLINE_COUNTRY = excel("Inputs", "D4")

HEADLINE = {
    7: ("LCOE (USD/MWh)", lambda c: results(c).lcoe_usd_per_mwh),
    8: ("LCOE (US cents/kWh)", lambda c: results(c).lcoe_cents_per_kwh),
    9: ("PPA tariff (US cents/kWh)", tariff_cents),
    10: ("Tariff minus LCOE (US cents/kWh)", lambda c: tariff_cents(c) - results(c).lcoe_cents_per_kwh),
    11: ("Project IRR", lambda c: results(c).project_irr),
    12: ("Equity IRR", lambda c: results(c).equity_irr),
    13: ("Project NPV (USD)", lambda c: results(c).project_npv),
    14: ("Minimum DSCR", lambda c: results(c).min_dscr),
    15: ("Average DSCR", lambda c: results(c).average_dscr),
    16: ("(section heading row)", None),
    17: ("Total capex (USD)", lambda c: results(c).total_capex),
    18: ("Capitalised interest (USD)", lambda c: results(c).capitalised_interest),
    19: ("Debt at COD (USD)", lambda c: results(c).debt_at_cod),
    20: ("Total equity (USD)", lambda c: results(c).equity),
    21: ("Effective gearing at COD", lambda c: results(c).effective_gearing_at_cod),
    22: ("Year-1 generation (MWh)", lambda c: results(c).year1_generation_mwh),
    23: ("Capacity factor", lambda c: results(c).capacity_factor),
}

SOLVE_FORS = {
    26: ("Tariff for target equity IRR (US cents/kWh)", solve.tariff_for_equity_irr),
    27: ("Tariff for target min DSCR (US cents/kWh)", solve.tariff_for_min_dscr),
    28: ("Implied discount rate", solve.implied_discount_rate),
}

SCENARIOS = {
    31: ("LCOE base (US cents/kWh)", "base"),
    32: ("LCOE conflict premium (US cents/kWh)", "conflict"),
    33: ("LCOE severe (US cents/kWh)", "severe"),
}

# Answer-key sensitivity labels -> engine driver names.
SENSITIVITY_LABELS = {
    "Capex": "Capex",
    "Discount rate": "Discount rate",
    "Specific yield (+/-10%)": "Specific yield",
    "Debt rate": "Debt rate",
    "Fixed O&M": "Fixed O&M",
    "Gearing": "Gearing",
    "Degradation": "Degradation",
    "DC/AC ratio": "DC/AC ratio",
}
SENSITIVITY_BLOCKS = {"KSA": range(38, 46), "UAE": range(48, 56)}
SENSITIVITY_COLUMNS = {
    "D": ("LCOE low", "lcoe_low"),
    "E": ("LCOE high", "lcoe_high"),
    "G": ("equity IRR low", "equity_irr_low"),
    "H": ("equity IRR high", "equity_irr_high"),
}


def build_checks():
    checks = []
    for row, (description, value) in HEADLINE.items():
        checks.append(
            ("Outputs", f"C{row}", f"{HEADLINE_COUNTRY} {description}",
             None if value is None else (lambda value=value: value(HEADLINE_COUNTRY)))
        )

    country_columns = {excel("Outputs", f"{col}25"): col for col in ("C", "D")}
    for country, col in country_columns.items():
        for row, (description, solver) in SOLVE_FORS.items():
            checks.append(
                ("Outputs", f"{col}{row}", f"{country} {description}",
                 lambda solver=solver, country=country: solver(country))
            )

    country_columns = {excel("Outputs", f"{col}30"): col for col in ("C", "D")}
    for country, col in country_columns.items():
        for row, (description, name) in SCENARIOS.items():
            checks.append(
                ("Outputs", f"{col}{row}", f"{country} {description}",
                 lambda name=name, country=country: solve.discount_scenarios(country)[name])
            )

    for country, rows in SENSITIVITY_BLOCKS.items():
        for row in rows:
            driver = SENSITIVITY_LABELS[excel("Outputs", f"A{row}")]
            for col, (description, column) in SENSITIVITY_COLUMNS.items():
                checks.append(
                    ("Outputs", f"{col}{row}", f"{country} {driver}: {description}",
                     lambda country=country, driver=driver, column=column:
                         sensitivities(country).loc[driver, column])
                )
    return checks


CHECKS = build_checks()


def test_sensitivity_blocks_are_labelled_as_expected():
    assert excel("Outputs", "A36") == "KSA"
    assert excel("Outputs", "A46") == "UAE"


@pytest.mark.parametrize(
    "sheet, cell, description, python_value",
    CHECKS,
    ids=[f"{cell} {description}" for _, cell, description, _ in CHECKS],
)
def test_matches_answer_key(sheet, cell, description, python_value, answer_key_report):
    expected = excel(sheet, cell)
    if expected is None or (isinstance(expected, str) and expected.startswith("#")):
        reason = "empty" if expected is None else f"Excel error {expected}"
        answer_key_report.append((cell, description, expected, None, None, f"SKIP ({reason})"))
        pytest.skip(f"{sheet}!{cell} is {reason}")

    actual = python_value()
    if actual is None:
        answer_key_report.append((cell, description, expected, None, None, "FAIL"))
        pytest.fail(f"{description}: Python returned no value; Excel has {expected}")

    actual = float(actual)
    difference = actual - expected
    passed = abs(difference) <= ABSOLUTE_TOLERANCE or abs(difference) <= RELATIVE_TOLERANCE * abs(expected)
    answer_key_report.append((cell, description, expected, actual, difference, "pass" if passed else "FAIL"))
    assert passed, f"{description}: Excel {expected}, Python {actual}, difference {difference}"
