"""The engine's annual table laid out as a grouped financial statement for the app.

Nothing here changes an engine value: each line is an engine column (or a sum or
product of engine columns) scaled to display units, with money out shown negative.
"""

from dataclasses import dataclass
from html import escape

import numpy as np
import pandas as pd

import ui_text as text
from model.engine import Results
from model.inputs import Inputs

MILLION = 1e-6
GWH = 1e-3  # MWh to GWh

# Decimal places shown for each unit.
DECIMALS = {"usd": 1, "gwh": 0, "cents": 2, "ratio": 2, "factor": 4}

MINUS = text.MINUS
SHADE = "#F7F4F8"
INK = "#141B26"
RULE = "#ECE7EF"


@dataclass(frozen=True)
class Line:
    section: str  # key in ui_text.STATEMENT_SECTIONS
    label: str
    unit: str  # key in DECIMALS
    values: np.ndarray  # one per period, display units, money out negative; NaN shows blank
    subtotal: bool = False
    summable: bool = True  # whether the Total column adds it up


def build_statement(inputs: Inputs, results: Results) -> list[Line]:
    """Every statement line, in display order, including the LCOE workings."""
    t = results.table
    operating = t["operating"].to_numpy()
    repayment = t["repayment"].to_numpy()

    def usd(column, sign=1):
        return sign * t[column].to_numpy() * MILLION

    lines_text = text.STATEMENT_LINES
    tax_label = text.COUNTRY_TAX_LINES[inputs.country]
    discounted_generation = t["generation_mwh"].to_numpy() * t["discount_factor"].to_numpy() * GWH

    return [
        Line("operations", lines_text["generation"], "gwh", t["generation_mwh"].to_numpy() * GWH),
        Line("operations", lines_text["tariff"], "cents",
             np.where(operating, inputs.ppa_tariff * 100, np.nan), summable=False),
        Line("operations", lines_text["revenue"], "usd", usd("revenue")),
        Line("operations", lines_text["fixed_om"], "usd", usd("om_cost", -1)),
        Line("operations", lines_text["ebitda"], "usd", usd("ebitda"), subtotal=True),

        Line("funding", lines_text["capex"], "usd", usd("capex_spend", -1)),
        Line("funding", lines_text["funded_by_debt"], "usd", usd("debt_drawdown")),
        Line("funding", lines_text["funded_by_equity"], "usd", usd("equity_contribution")),
        Line("funding", lines_text["capitalised_interest"], "usd", usd("capitalised_interest")),
        Line("funding", lines_text["total_debt_drawn"], "usd",
             usd("debt_drawdown") + usd("capitalised_interest"), subtotal=True),

        Line("debt", lines_text["opening_balance"], "usd", usd("opening_balance"), summable=False),
        Line("debt", lines_text["drawdowns"], "usd", usd("debt_drawdown") + usd("capitalised_interest")),
        Line("debt", lines_text["interest_paid"], "usd", usd("interest_paid", -1)),
        Line("debt", lines_text["principal_repaid"], "usd", usd("principal_repaid", -1)),
        Line("debt", lines_text["closing_balance"], "usd", usd("closing_balance"), subtotal=True, summable=False),

        Line("tax", lines_text["depreciation"], "usd", usd("depreciation")),
        Line("tax", lines_text["taxable_income"], "usd", usd("taxable_income")),
        Line("tax", tax_label, "usd", usd("tax", -1)),
        Line("tax", lines_text["unlevered_tax"], "usd", usd("unlevered_tax", -1)),
        Line("tax", lines_text["tax_paid"], "usd", usd("tax", -1), subtotal=True),

        Line("cover", text.CASH_FLOW_EBITDA, "usd", usd("ebitda")),
        Line("cover", text.CASH_FLOW_TAX, "usd", usd("tax", -1)),
        Line("cover", lines_text["cfads"], "usd", usd("cfads"), subtotal=True),
        Line("cover", lines_text["debt_service"], "usd", usd("debt_service", -1)),
        Line("cover", lines_text["dscr"], "ratio",
             np.where(repayment, t["dscr"].to_numpy(), np.nan), summable=False),

        Line("returns", lines_text["equity_contribution"], "usd", usd("equity_contribution", -1)),
        Line("returns", lines_text["equity_cash_flow"], "usd", usd("equity_cash_flow"), subtotal=True),
        Line("returns", lines_text["project_cash_flow"], "usd", usd("project_cash_flow"), subtotal=True),

        Line("lcoe", lines_text["discount_factor"], "factor", t["discount_factor"].to_numpy(), summable=False),
        Line("lcoe", lines_text["discounted_capex"], "usd",
             usd("capex_spend", -1) * t["discount_factor"].to_numpy()),
        Line("lcoe", lines_text["discounted_om"], "usd", usd("om_cost", -1) * t["discount_factor"].to_numpy()),
        Line("lcoe", lines_text["discounted_generation"], "gwh", discounted_generation),
    ]


def total(line: Line) -> float:
    """The Total column: a sum for flows, blank (NaN) for balances, prices, ratios and factors."""
    return float(np.nansum(line.values)) if line.summable else np.nan


def column_labels(inputs: Inputs, results: Results) -> list[str]:
    """Y1 build, Y2 build, Y3 (op 1), ..."""
    labels = []
    for period, row in results.table.iterrows():
        if row["construction"]:
            labels.append(text.BUILD_YEAR.format(period=period))
        else:
            labels.append(text.OPERATING_YEAR.format(period=period, year=row["operating_year"]))
    return labels


def key_year_positions(inputs: Inputs, results: Results) -> list[int]:
    """Column positions for the key-years view: build years, operating years 1, 2, 5,
    10 and 20, the last debt year and the final year."""
    build = inputs.construction_years
    operating_years = {1, 2, 5, 10, 20, inputs.debt_tenor, inputs.ppa_term}
    positions = list(range(build)) + [build + year - 1 for year in sorted(operating_years) if year <= inputs.ppa_term]
    return positions


def number(value: float, unit: str) -> str:
    """A display number with a true minus sign; blank for NaN."""
    if value is None or np.isnan(value):
        return ""
    decimals = DECIMALS[unit]
    value = round(float(value), decimals)
    sign = MINUS if value < 0 else ""
    return f"{sign}{abs(value):,.{decimals}f}"


def to_csv(lines: list[Line], columns: list[str]) -> str:
    """All years, one row per line: Section, Line, Unit, then one column per year."""
    rows = [
        [text.STATEMENT_SECTIONS[line.section], line.label, text.STATEMENT_UNITS[line.unit],
         *np.round(line.values, 6)]
        for line in lines
    ]
    return pd.DataFrame(rows, columns=[*text.CASH_FLOWS_CSV_COLUMNS, *columns]).to_csv(index=False)


STYLE = f"""
<style>
.cf-wrap {{ overflow-x: auto; border: 1px solid {RULE}; border-radius: 6px; }}
.cf-table {{ border-collapse: separate; border-spacing: 0; font-size: 13px; color: {INK};
  font-variant-numeric: tabular-nums; white-space: nowrap; width: max-content; min-width: 100%; }}
.cf-table th, .cf-table td {{ padding: 4px 10px; text-align: right; border-bottom: 1px solid {RULE};
  background: #FFFFFF; }}
.cf-table thead th {{ font-weight: 600; border-bottom: 2px solid {RULE}; }}
.cf-table .cf-line {{ position: sticky; left: 0; z-index: 1; text-align: left; white-space: normal;
  min-width: 170px; max-width: 230px; border-right: 1px solid {RULE}; font-weight: 400; }}
.cf-table .cf-total {{ border-right: 1px solid {RULE}; }}
.cf-table thead th.cf-line, .cf-table thead th.cf-total {{ font-weight: 600; }}
.cf-table tr.cf-section > * {{ background: {SHADE}; font-weight: 700; }}
.cf-table tr.cf-subtotal > * {{ font-weight: 700; border-top: 1px solid {INK}; }}
</style>
"""


def to_html(lines: list[Line], columns: list[str], positions: list[int], show_lcoe: bool) -> str:
    """The statement as an HTML table: pinned line names, a Total column, shaded section rows."""
    shown = [columns[p] for p in positions]
    head = "".join(f"<th>{escape(c)}</th>" for c in shown)
    body = []
    section = None
    for line in lines:
        if line.section == "lcoe" and not show_lcoe:
            continue
        if line.section != section:
            section = line.section
            blanks = "<td></td>" * (len(shown) + 1)
            body.append(
                f'<tr class="cf-section"><th class="cf-line" scope="rowgroup">'
                f"{escape(text.STATEMENT_SECTIONS[section])}</th>{blanks}</tr>"
            )
        cells = "".join(f"<td>{number(line.values[p], line.unit)}</td>" for p in positions)
        row_class = ' class="cf-subtotal"' if line.subtotal else ""
        body.append(
            f'<tr{row_class}><th class="cf-line" scope="row">{escape(line.label)}</th>'
            f'<td class="cf-total">{number(total(line), line.unit)}</td>{cells}</tr>'
        )
    return (
        f'{STYLE}<div class="cf-wrap"><table class="cf-table"><thead><tr>'
        f'<th class="cf-line">{escape(text.CASH_FLOWS_LINE_HEADER)}</th>'
        f'<th class="cf-total">{escape(text.CASH_FLOWS_TOTAL_HEADER)}</th>{head}</tr></thead>'
        f'<tbody>{"".join(body)}</tbody></table></div>'
    )
