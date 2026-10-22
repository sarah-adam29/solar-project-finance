"""Checks on the cash-flow statement shown in the app (statement.py).

The statement only rearranges engine values, so these check that it adds up and
that its totals match the engine table.
"""

import numpy as np
import pytest

import statement
import ui_text as text
from model.engine import run_model
from model.inputs import load_inputs

TOLERANCE = 1e-9
LINES = text.STATEMENT_LINES

# Base cases plus a case away from the base, so the checks aren't tied to one set of numbers.
CASES = [
    ("KSA", {}),
    ("UAE", {}),
    ("KSA", {"capex": 700, "ppa_tariff": 0.015, "debt_tenor": 28}),
    ("UAE", {"specific_yield_year1": 2464, "gearing": 0.65, "debt_rate": 0.05}),
]
IDS = [f"{country} {'base' if not overrides else 'changed'}" for country, overrides in CASES]


def build(country, overrides):
    inputs = load_inputs(country, overrides)
    results = run_model(inputs)
    lines = statement.build_statement(inputs, results)
    return inputs, results, lines


def line(lines, section, label):
    matches = [item for item in lines if item.section == section and item.label == label]
    assert len(matches) == 1, f"{section}: {label}"
    return matches[0].values


@pytest.mark.parametrize("country, overrides", CASES, ids=IDS)
def test_revenue_minus_om_is_ebitda(country, overrides):
    _, _, lines = build(country, overrides)
    revenue = line(lines, "operations", LINES["revenue"])
    fixed_om = line(lines, "operations", LINES["fixed_om"])  # shown negative
    ebitda = line(lines, "operations", LINES["ebitda"])
    assert np.allclose(revenue + fixed_om, ebitda, atol=TOLERANCE)


@pytest.mark.parametrize("country, overrides", CASES, ids=IDS)
def test_ebitda_minus_tax_is_cfads(country, overrides):
    _, _, lines = build(country, overrides)
    ebitda = line(lines, "cover", text.CASH_FLOW_EBITDA)
    tax = line(lines, "cover", text.CASH_FLOW_TAX)  # shown negative
    cfads = line(lines, "cover", LINES["cfads"])
    assert np.allclose(ebitda + tax, cfads, atol=TOLERANCE)


# Statement lines that are a single engine column: (section, label, column, sign, scale).
ENGINE_COLUMNS = [
    ("operations", LINES["generation"], "generation_mwh", 1, statement.GWH),
    ("operations", LINES["revenue"], "revenue", 1, statement.MILLION),
    ("operations", LINES["fixed_om"], "om_cost", -1, statement.MILLION),
    ("operations", LINES["ebitda"], "ebitda", 1, statement.MILLION),
    ("funding", LINES["capex"], "capex_spend", -1, statement.MILLION),
    ("funding", LINES["funded_by_debt"], "debt_drawdown", 1, statement.MILLION),
    ("funding", LINES["funded_by_equity"], "equity_contribution", 1, statement.MILLION),
    ("funding", LINES["capitalised_interest"], "capitalised_interest", 1, statement.MILLION),
    ("debt", LINES["interest_paid"], "interest_paid", -1, statement.MILLION),
    ("debt", LINES["principal_repaid"], "principal_repaid", -1, statement.MILLION),
    ("tax", LINES["depreciation"], "depreciation", 1, statement.MILLION),
    ("tax", LINES["taxable_income"], "taxable_income", 1, statement.MILLION),
    ("tax", LINES["unlevered_tax"], "unlevered_tax", -1, statement.MILLION),
    ("tax", LINES["tax_paid"], "tax", -1, statement.MILLION),
    ("cover", LINES["cfads"], "cfads", 1, statement.MILLION),
    ("cover", LINES["debt_service"], "debt_service", -1, statement.MILLION),
    ("returns", LINES["equity_contribution"], "equity_contribution", -1, statement.MILLION),
    ("returns", LINES["equity_cash_flow"], "equity_cash_flow", 1, statement.MILLION),
    ("returns", LINES["project_cash_flow"], "project_cash_flow", 1, statement.MILLION),
]


@pytest.mark.parametrize("country, overrides", CASES, ids=IDS)
def test_totals_match_the_engine(country, overrides):
    inputs, results, lines = build(country, overrides)
    table = results.table
    by_label = {(item.section, item.label): item for item in lines}

    for section, label, column, sign, scale in ENGINE_COLUMNS:
        expected = sign * table[column].sum() * scale
        assert statement.total(by_label[(section, label)]) == pytest.approx(expected, abs=TOLERANCE), label

    # The country's own tax line, and the lines built from two engine columns.
    tax_line = by_label[("tax", text.COUNTRY_TAX_LINES[country])]
    assert statement.total(tax_line) == pytest.approx(-table["tax"].sum() * statement.MILLION, abs=TOLERANCE)
    drawn = (table["debt_drawdown"].sum() + table["capitalised_interest"].sum()) * statement.MILLION
    assert statement.total(by_label[("funding", LINES["total_debt_drawn"])]) == pytest.approx(drawn, abs=TOLERANCE)
    assert statement.total(by_label[("debt", LINES["drawdowns"])]) == pytest.approx(drawn, abs=TOLERANCE)

    # The LCOE workings reproduce the engine's LCOE.
    discounted_costs = (statement.total(by_label[("lcoe", LINES["discounted_capex"])])
                        + statement.total(by_label[("lcoe", LINES["discounted_om"])]))
    discounted_gwh = statement.total(by_label[("lcoe", LINES["discounted_generation"])])
    lcoe_usd_per_mwh = -discounted_costs / discounted_gwh * 1000  # USD m per GWh -> USD per MWh
    assert lcoe_usd_per_mwh == pytest.approx(results.lcoe_usd_per_mwh, rel=1e-12)

    # Balances, prices, ratios and factors have no total.
    for section, label in (("debt", LINES["opening_balance"]), ("debt", LINES["closing_balance"]),
                           ("operations", LINES["tariff"]), ("cover", LINES["dscr"]),
                           ("lcoe", LINES["discount_factor"])):
        assert np.isnan(statement.total(by_label[(section, label)])), label


@pytest.mark.parametrize("country", ["KSA", "UAE"])
def test_only_the_selected_countrys_tax_line_shows(country):
    _, _, lines = build(country, {})
    labels = {item.label for item in lines}
    other = "UAE" if country == "KSA" else "KSA"
    assert text.COUNTRY_TAX_LINES[country] in labels
    assert text.COUNTRY_TAX_LINES[other] not in labels


@pytest.mark.parametrize("country, last_debt_year, final_year", [("KSA", 30, 35), ("UAE", 27, 30)])
def test_key_years_and_column_labels(country, last_debt_year, final_year):
    inputs, results, _ = build(country, {})
    columns = statement.column_labels(inputs, results)
    assert columns[:3] == ["Y1 build", "Y2 build", "Y3 (op 1)"]
    shown = [columns[p] for p in statement.key_year_positions(inputs, results)]
    operating = [f"(op {year})" for year in (1, 2, 5, 10, 20, last_debt_year, final_year)]
    assert shown[:2] == ["Y1 build", "Y2 build"]
    assert [label.split(" ", 1)[1] for label in shown[2:]] == operating


def test_dscr_is_blank_outside_repayment_years():
    inputs, results, lines = build("KSA", {})
    dscr = line(lines, "cover", LINES["dscr"])
    repayment = results.table["repayment"].to_numpy()
    assert np.all(np.isnan(dscr[~repayment]))
    assert not np.any(np.isnan(dscr[repayment]))


def test_csv_has_all_years_in_long_format():
    inputs, results, lines = build("UAE", {})
    columns = statement.column_labels(inputs, results)
    csv = statement.to_csv(lines, columns).splitlines()
    assert csv[0] == ",".join([*text.CASH_FLOWS_CSV_COLUMNS, *columns])
    assert len(csv) == 1 + len(lines)
    assert len(columns) == inputs.construction_years + inputs.ppa_term


def test_negative_numbers_use_a_true_minus_sign():
    assert statement.number(-12.34, "usd") == "−12.3"
    assert statement.number(-0.00001, "usd") == "0.0"
    assert statement.number(float("nan"), "usd") == ""
