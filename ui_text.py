"""All user-facing text in the Streamlit app, so wording can be edited in one place."""

# --- Page -----------------------------------------------------------------

PAGE_TITLE = "Gulf solar tariffs and the cost of capital"
TITLE = "What do Gulf solar tariffs imply about the cost of capital?"
INTRO = (
    "A project finance model of utility-scale solar in Saudi Arabia and the UAE, "
    "built from public data and checked against a hand-built Excel model."
)

# Shown word for word in a notice under the title, in the Method expander and
# in the footer, and in the README. Never remove or shorten it.
GITHUB_ISSUES_URL = "https://github.com/sarah-adam29/solar-project-finance/issues"
LINKEDIN_URL = "https://www.linkedin.com/in/sarah-adam-a24949b1/"
DISCLAIMER = (
    "Personal learning project, not investment advice. I built this model myself from public "
    "sources to learn project finance modelling and Python. It has not been reviewed or validated "
    "by industry experts, developers, lenders or other market participants, and its results may "
    "be wrong. Please don't use it for investment, lending or policy decisions. If you have better "
    "data or spot an error, I'd be glad to hear from you: "
    f"[open an issue on GitHub]({GITHUB_ISSUES_URL}) or [message me on LinkedIn]({LINKEDIN_URL})."
)

FIXED_ASSUMPTIONS = (
    "Fixed in this model: {capacity:,.0f} MWac plant · {ppa_term}-year PPA · "
    "{construction_years}-year build · USD, nominal · valued at financial close"
)
FIXED_ASSUMPTIONS_HELP = (
    "These are held constant. Changing plant size wouldn't change LCOE, IRRs or DSCR in this "
    "model, because costs and output are per kW. PPA term flexibility is planned for v2."
)

# --- Sidebar --------------------------------------------------------------

COUNTRY_LABEL = "Country"
RESET_BUTTON = "Reset to base case"
RANGES_NOTE = (
    "Ranges from public sources, widened slightly where a source gives a single value; see Method."
)

# Sidebar groups, in display order: (header, caption, slider parameters).
GROUPS = [
    ("Revenue", "What the project is paid", ["ppa_tariff"]),
    ("Costs", "What it costs to build and run", ["capex", "fixed_om"]),
    (
        "Plant performance",
        "How much electricity it produces",
        ["specific_yield_year1", "degradation", "dc_ac_ratio"],
    ),
    ("Financing", "How the build is paid for", ["gearing", "debt_rate", "debt_tenor"]),
    ("Valuation", "The return investors require", ["discount_rate"]),
]

SLIDER_LABELS = {
    "ppa_tariff": "PPA tariff (US cents/kWh)",
    "capex": "Capex (USD/kWac)",
    "fixed_om": "Fixed O&M (USD/kWac per year)",
    "specific_yield_year1": "Specific yield, year 1 (kWh/kWp)",
    "degradation": "Degradation (% per year)",
    "dc_ac_ratio": "DC/AC ratio",
    "gearing": "Gearing (% debt)",
    "debt_rate": "Debt rate (%)",
    "debt_tenor": "Debt tenor (years)",
    "discount_rate": "Discount rate, cost of capital (%)",
}

# Base case value with its unit, shown first in each slider tooltip.
BASE_CASE = "Base case: {value}"
BASE_CASE_FORMATS = {
    "ppa_tariff": "{:.2f} US cents/kWh",
    "capex": "{:,.0f} USD/kWac",
    "fixed_om": "{:g} USD/kWac per year",
    "specific_yield_year1": "{:,.0f} kWh/kWp",
    "degradation": "{:g}% per year",
    "dc_ac_ratio": "{:.2f}",
    "gearing": "{:.0f}% debt",
    "debt_rate": "{:.1f}%",
    "debt_tenor": "{} years",
    "discount_rate": "{:.1f}%",
}

# How each input type from data/assumptions.csv is described after its source.
TYPE_LABELS = {
    "public": "public source",
    "derived": "derived from public sources",
    "judgment": "judgment",
    "invented": "invented",
}

# --- Definitions ----------------------------------------------------------

# Glossary terms for the inputs, in sidebar order: (term, slider parameter, definition).
INPUT_TERMS = [
    (
        "PPA tariff",
        "ppa_tariff",
        "The fixed price the buyer pays for each kWh under the power purchase agreement (PPA), "
        "the long-term sales contract that runs for 25–35 years in these tenders.",
    ),
    (
        "Capex",
        "capex",
        "The upfront cost to build the plant (panels, inverters, trackers, grid connection), "
        "per kW of AC capacity.",
    ),
    (
        "Fixed O&M",
        "fixed_om",
        "The yearly cost of operating and maintaining the plant (cleaning, repairs, staff), "
        "per kW of AC capacity.",
    ),
    (
        "Specific yield",
        "specific_yield_year1",
        "Electricity produced in a year for each kW of solar panels (kWh/kWp). Higher in sunnier "
        "places and with sun-tracking mounts.",
    ),
    ("Degradation", "degradation", "The share of output panels lose each year as they age."),
    (
        "DC/AC ratio",
        "dc_ac_ratio",
        "Panel capacity relative to inverter (grid-connection) capacity. Fitting more panels than "
        "the connection allows squeezes more energy out of it.",
    ),
    ("Gearing", "gearing", "The share of the build cost funded by debt rather than shareholders."),
    ("Debt rate", "debt_rate", "The all-in annual interest rate on the project loan."),
    ("Debt tenor", "debt_tenor", "The number of years over which the loan is repaid."),
    (
        "Discount rate (cost of capital)",
        "discount_rate",
        "The annual return investors require. Used to value future cash flows in today's money.",
    ),
]

# Glossary terms for the inputs held constant: (term, key, definition).
FIXED_TERMS = [
    (
        "PPA term",
        "ppa_term",
        "How long the power purchase agreement runs. The plant is assumed to operate for exactly "
        "this long.",
    ),
    (
        "Plant size (MWac)",
        "capacity",
        "The plant's grid-connection capacity. Costs and output are per kW, so size doesn't change "
        "the unit economics here.",
    ),
]

# Glossary terms for the outputs: (term, key, definition).
OUTPUT_TERMS = [
    (
        "LCOE",
        "lcoe",
        "Levelised cost of electricity: the constant price per kWh that exactly covers the "
        "plant's build and running costs over its life, at the chosen cost of capital. It excludes "
        "tax and financing structure.",
    ),
    (
        "Implied cost of capital",
        "implied_rate",
        "The cost of capital at which the LCOE equals the awarded tariff, i.e. the return the "
        "tariff actually pays for.",
    ),
    ("Project IRR", "project_irr", "The annual return on the whole project after tax, before any debt."),
    (
        "Equity IRR",
        "equity_irr",
        "The annual return to shareholders after paying the debt. Negative means shareholders "
        "get back less than they put in.",
    ),
    (
        "Minimum DSCR",
        "min_dscr",
        "Debt service coverage ratio: cash available in a year divided by the debt payment due, "
        "at its lowest year. Lenders usually require at least 1.20×; below 1.0× the project "
        "can't cover its debt from operations.",
    ),
    (
        "NPV",
        "npv",
        "The value of the project's cash flows at financial close (the day the loans are signed "
        "and construction starts, two years before the plant runs), at the chosen cost of capital. "
        "Negative means the project returns less than that rate.",
    ),
]

INPUT_DEFINITIONS = {parameter: definition for _, parameter, definition in INPUT_TERMS}
OUTPUT_DEFINITIONS = {key: definition for _, key, definition in OUTPUT_TERMS}

# --- Metric tiles ---------------------------------------------------------

# In display order: the cost row, then the returns and debt row.
TILE_LABELS = {
    "lcoe": "LCOE (US cents/kWh)",
    "implied_rate": "Implied cost of capital",
    "npv": "Project NPV",
    "project_irr": "Project IRR",
    "equity_irr": "Equity IRR",
    "min_dscr": "Minimum DSCR",
}
# Caption under the implied cost of capital tile, by the CSV type of the
# country's base discount rate. UAE's base is a judgment between two sources,
# so it is not called a published estimate.
DISCOUNT_RATE_CAPTIONS = {
    "public": "Published estimate: {rate:.1f}% (Hatton et al. 2026)",
    "judgment": "Base-case estimate: {rate:.1f}% (judgment)",
}
AWARDED_TARIFF = "Awarded tariff: {tariff:.2f} US cents/kWh"
NOT_MEANINGFUL = "n.m."
NOT_MEANINGFUL_REASONS = {
    "project_irr": "n.m.: the project never pays back.",
    "equity_irr": "n.m.: equity is never paid back.",
}
NPV_DATE = "Valued at financial close, covering all cash flows to the end of the PPA"
VERSUS_BASE = "{difference} vs base"
MINUS = "\u2212"  # true minus sign for negative numbers

FOOTER_HEADING = "Disclaimer and feedback"

GLOSSARY_TITLE = "What the terms mean"
GLOSSARY_INPUTS = "Inputs"
GLOSSARY_FIXED = "Fixed in this model"
GLOSSARY_OUTPUTS = "Outputs"

# --- Charts ---------------------------------------------------------------

# The finding: LCOE across discount rates against the tariff.
FINDING_TITLE = "In this model, awarded tariffs only cover costs at about {rate}"
FINDING_TITLE_CHANGED_TARIFF = "In this model, a {tariff:.2f}-cent tariff covers costs at about {rate}"
FINDING_TITLE_NO_CROSSING = "In this model, the tariff and the LCOE line don't cross at any cost of capital the model can test"
FINDING_CAPTION = (
    "The line is the LCOE at each cost of capital, with every other input as set in the sidebar. "
    "In this model, where it crosses the tariff is the return the tariff actually pays for."
)
FINDING_X_AXIS = "Cost of capital (discount rate)"
FINDING_Y_AXIS = "US cents/kWh"
FINDING_LCOE_LINE = "LCOE"
FINDING_TARIFF_LINE = "Awarded tariff: {tariff:.2f}"
FINDING_TARIFF_LINE_CHANGED = "Tariff: {tariff:.2f}"
FINDING_CROSSING = "Implied cost of capital: {rate}"
# Discount-rate scenarios marked on the LCOE line: premium in bp, then LCOE.
FINDING_SCENARIOS = {
    "conflict": "Conflict +{bp:.0f}bp: {lcoe}",
    "severe": "Severe +{bp:.0f}bp: {lcoe}",
}
FINDING_SCENARIO_NOTE = (
    "The two marked points add the conflict (+{conflict:.0f}bp) and severe (+{severe:.0f}bp) "
    "premiums to the discount rate set in the sidebar (judgment)."
)
# Shaded discount-rate range from the CSV (low, high, base), by the type of the
# country's base rate.
FINDING_BAND = {
    "public": "Estimate range {low}–{high}% (base {base}%)",
    "judgment": "Estimate range {low}–{high}% (base {base}%, judgment)",
}
FINDING_GAP = "Gap: {gap} pp"

# Tornado: which inputs move the answer most.
TORNADO_TITLE = "Which assumptions move the answer most"
TORNADO_MEASURE_LABEL = "Measure"
TORNADO_MEASURES = {"lcoe": "LCOE", "equity_irr": "Equity IRR"}
TORNADO_CAPTION = (
    "Each bar shows the {measure} with one input at the low or high end of its source range, "
    "everything else as set in the sidebar. The label at each bar end is the input value that "
    "produced it. Sorted by total swing."
)
TORNADO_TOP_NOTE = (
    "Top {shown} of {total} drivers. Debt rate and gearing don't affect LCOE in this model."
)
TORNADO_IMPROVES = "Improves the project"
TORNADO_WORSENS = "Worsens the project"
TORNADO_BASE_LINE = {"base": "Base case: {value}", "changed": "Your inputs: {value}"}
TORNADO_AXIS = {"lcoe": "LCOE (US cents/kWh)", "equity_irr": "Equity IRR"}
TORNADO_NO_BASE = "Equity IRR can't be calculated for these inputs (equity is never paid back), so there is no tornado to show."
# Engine driver names -> chart labels.
TORNADO_DRIVERS = {
    "Capex": "Capex",
    "Discount rate": "Discount rate (cost of capital)",
    "Specific yield": "Specific yield (kWh/kWp)",
    "Debt rate": "Debt rate",
    "Fixed O&M": "Fixed O&M",
    "Gearing": "Gearing",
    "Degradation": "Degradation",
    "DC/AC ratio": "DC/AC ratio",
}
# Input value at each bar end, after the app converts it to display units.
TORNADO_INPUT_FORMATS = {
    "Capex": "${:,.0f}/kW",
    "Discount rate": "{:.1f}%",
    "Specific yield": "{:,.0f}",  # unit is in the driver name, to keep labels short
    "Debt rate": "{:.1f}%",
    "Fixed O&M": "${:g}/kW/yr",
    "Gearing": "{:.0f}% debt",
    "Degradation": "{:g}%/yr",
    "DC/AC ratio": "{:.2f}",
}

# Tariff investors would need.
TARIFF_TITLE = "What tariff would investors need?"
TARIFF_CAPTION = "US cents/kWh needed to reach each target, with every other input as set in the sidebar."
TARIFF_BARS = {
    "tariff": "Awarded tariff",
    "tariff_changed": "Tariff (your input)",
    "equity_irr": "For an {target:.0f}% equity IRR",
    "min_dscr": "For a {target:.2f}× minimum DSCR",
}
# Value at the end of each target bar, with its uplift on the awarded tariff.
TARIFF_VALUE_WITH_UPLIFT = "{value} ({uplift})"

# --- Trust line -----------------------------------------------------------

# Number of answer-key values the tests compare (tests/test_app.py checks it
# against tests/test_answer_key.py, so update both together).
ANSWER_KEY_CHECKS = 92
TRUST_LINE = "Python engine verified against a hand-built Excel model: {checks} checks within 0.1%"

# --- Annual cash flows ----------------------------------------------------

CASH_FLOWS_TITLE = "Annual cash flows"
CASH_FLOWS_CAPTION = (
    "USD millions, nominal, unless stated. Money out is negative. The Total column covers all "
    "years. Inputs as set in the sidebar."
)
CASH_FLOWS_VIEW_LABEL = "Years shown"
CASH_FLOWS_VIEWS = {"key": "Key years", "all": "All years"}
CASH_FLOWS_LCOE_TOGGLE = "Show LCOE workings"
CASH_FLOWS_DOWNLOAD = "Download all years as CSV"
CASH_FLOWS_FILE = "solar_cash_flows_{country}.csv"
CASH_FLOWS_LINE_HEADER = "Line"
CASH_FLOWS_TOTAL_HEADER = "Total"
CASH_FLOWS_CSV_COLUMNS = ("Section", "Line", "Unit")
BUILD_YEAR = "Y{period} build"
OPERATING_YEAR = "Y{period} (op {year})"

# Statement sections, in display order.
STATEMENT_SECTIONS = {
    "operations": "Operations",
    "funding": "Construction and funding",
    "debt": "Debt",
    "tax": "Tax",
    "cover": "Cash flow and debt cover",
    "returns": "Returns",
    "lcoe": "LCOE workings",
}
# Statement lines: key -> label. The country's tax line is chosen by country.
STATEMENT_LINES = {
    "generation": "Generation (GWh)",
    "tariff": "Tariff (US cents/kWh)",
    "revenue": "Revenue",
    "fixed_om": "Fixed O&M",
    "ebitda": "EBITDA",
    "capex": "Capex",
    "funded_by_debt": "Funded by debt",
    "funded_by_equity": "Funded by equity",
    "capitalised_interest": "Interest during construction (capitalised)",
    "total_debt_drawn": "Total debt drawn",
    "opening_balance": "Opening balance",
    "drawdowns": "Drawdowns incl. capitalised interest",
    "interest_paid": "Interest paid",
    "principal_repaid": "Principal repaid",
    "closing_balance": "Closing balance",
    "depreciation": "Depreciation",
    "taxable_income": "Taxable income",
    "unlevered_tax": "Unlevered tax (for project returns)",
    "tax_paid": "Tax paid",
    "cfads": "CFADS",
    "debt_service": "Debt service",
    "dscr": "DSCR (x)",
    "equity_contribution": "Equity contribution",
    "equity_cash_flow": "Equity cash flow",
    "project_cash_flow": "Project cash flow",
    "discount_factor": "Discount factor",
    "discounted_capex": "Discounted capex",
    "discounted_om": "Discounted O&M",
    "discounted_generation": "Discounted generation (GWh)",
}
COUNTRY_TAX_LINES = {"KSA": "KSA income tax and zakat", "UAE": "UAE corporate tax"}
# Repeated lines in the cash flow section.
CASH_FLOW_EBITDA = "EBITDA"
CASH_FLOW_TAX = "Tax"
# Units in the CSV download.
STATEMENT_UNITS = {
    "usd": "USD m",
    "gwh": "GWh",
    "cents": "US cents/kWh",
    "ratio": "x",
    "factor": "factor",
}

# --- Method and limitations -----------------------------------------------

METHOD_TITLE = "Method and limitations"
REPO_URL = "https://github.com/sarah-adam29/solar-project-finance"
ANSWER_KEY_URL = f"{REPO_URL}/blob/main/excel/solar_answer_key.xlsx"

# Readable names for every input in data/assumptions.csv.
PARAMETER_NAMES = {
    "capacity": "Plant size",
    "dc_ac_ratio": "DC/AC ratio",
    "specific_yield_year1": "Specific yield",
    "degradation": "Degradation",
    "construction_years": "Construction period",
    "capex_phase_y1": "Capex spent in build year 1",
    "capex_phase_y2": "Capex spent in build year 2",
    "capex": "Capex",
    "fixed_om": "Fixed O&M",
    "ppa_tariff": "PPA tariff",
    "ppa_term": "PPA term",
    "gearing": "Gearing",
    "debt_tenor": "Debt tenor",
    "debt_rate": "Debt rate",
    "discount_rate": "Discount rate",
    "project_life": "Project life",
    "target_equity_irr": "Target equity IRR",
    "target_min_dscr": "Target minimum DSCR",
    "conflict_premium": "Conflict premium",
    "severe_premium": "Severe premium",
    "corporate_income_tax": "KSA income tax",
    "zakat": "Zakat",
    "foreign_ownership_share": "Foreign ownership share",
    "corporate_tax": "UAE corporate tax",
    "uae_tax_threshold": "UAE tax threshold",
    "aed_per_usd": "AED per USD",
}

METHOD_HOW = """**How the model works**

- **Timeline.** Annual periods. Period 1 is financial close, when the loans are signed and construction starts. Construction takes {construction_years} years, with {phase_y1:.0f}% of capex spent in the first year and {phase_y2:.0f}% in the second. The plant then runs for the PPA term: {ppa_terms}.
- **Funding.** During construction, capex is paid by debt and equity in proportion to the gearing. Interest during construction is added to the loan.
- **Debt.** The loan is repaid as an annuity (equal yearly payments of interest plus principal) over the debt tenor. The payment is worked out once, on the balance at the commercial operation date (COD).
- **Revenue and costs.** Generation is plant size × DC/AC ratio × specific yield, falling each year by the degradation rate. Revenue is generation × tariff. The tariff and O&M are flat in nominal terms.
- **Tax.** KSA: 20% income tax on the foreign-owned share of taxable profit and 2.5% zakat on the Saudi share (v1 applies zakat to profit). UAE: 9% corporate tax on taxable income above AED 375,000. Depreciation is straight-line over the project life, on capex plus capitalised interest.
- **LCOE.** Discounted capex plus discounted O&M, divided by discounted generation, at the discount rate. It excludes tax and financing structure.
- **Returns.** Project IRR uses cash flows after tax and before debt, with tax worked out as if there were no debt. Equity IRR uses cash flows to shareholders after debt service and tax. NPV discounts project cash flows to financial close, with each year's cash flow at the end of that year.
- **Solve-fors.** The implied cost of capital is the discount rate at which the LCOE equals the tariff. The tariffs for the equity IRR and DSCR targets are found the same way, by searching for the value that hits the target.
- **Sensitivities and scenarios.** The tornado moves one input at a time to the low and high end of its source range, with everything else as set in the sidebar. The conflict and severe scenarios add {conflict_bp:.0f}bp and {severe_bp:.0f}bp to the discount rate.
- **Checks.** The Python engine is tested against a hand-built Excel model: {checks} values must match within 0.1%."""

METHOD_FIXED = """**Fixed in this model**

The plant size ({capacity:,.0f} MWac) is an invented reference size so the two countries compare like for like. Costs and output are per kW, so it doesn't change LCOE, IRRs or DSCR; it only scales NPV and the cash-flow table."""

METHOD_JUDGMENT_HEADING = "**Judgment and invented inputs**"
METHOD_JUDGMENT_INTRO = (
    "Every input in data/assumptions.csv is labelled public, derived, judgment or invented. "
    "These are the author's own judgment or invented:"
)
METHOD_JUDGMENT_ITEM = "- {name} ({countries}): {type}"

METHOD_WIDENED_HEADING = "**Slider ranges**"
METHOD_WIDENED_INTRO = (
    "Each slider runs from the low to the high value in data/assumptions.csv. Where the source "
    "range starts or ends at the base case, the slider is widened by mirroring the other side, so "
    "it can move both ways from the base case:"
)
METHOD_WIDENED_ITEM = "- {country} {name}: {end} end widened from {csv} to {slider} {unit}"
METHOD_WIDENED_ENDS = {"low": "low", "high": "high"}

METHOD_LIMITATIONS = """**Limitations (v1)**

- Flat tariff and O&M.
- All capacity reaches COD together (no phased COD).
- Pro-rata debt/equity funding during construction.
- Interest during construction capitalised into debt.
- No DSRA.
- No tax-loss carry-forward.
- Zakat approximated as 2.5% of profit.
- Construction period fixed at 2 years."""

METHOD_LINKS = f"""**Code and answer key**

- [GitHub repository]({REPO_URL})
- [Excel answer key]({ANSWER_KEY_URL})"""

METHOD_DISCLAIMER_HEADING = "**Disclaimer**"


def method_markdown(facts: dict, judgment_items: list[str], widened_items: list[str]) -> str:
    """The Method and limitations text, shared by the app and the README."""
    return "\n\n".join([
        METHOD_HOW.format(**facts),
        METHOD_FIXED.format(**facts),
        "\n".join([METHOD_JUDGMENT_HEADING, "", METHOD_JUDGMENT_INTRO, "", *judgment_items]),
        "\n".join([METHOD_WIDENED_HEADING, "", METHOD_WIDENED_INTRO, "", *widened_items]),
        METHOD_LIMITATIONS,
        METHOD_LINKS,
        "\n".join([METHOD_DISCLAIMER_HEADING, "", DISCLAIMER]),
    ])


# The README has its own Limitations and Disclaimer sections, so its Method
# section leaves out those blocks and the links, and points to the answer key.
README_ANSWER_KEY = "Excel answer key: [excel/solar_answer_key.xlsx](excel/solar_answer_key.xlsx)"


def readme_method_markdown(app_method: str) -> str:
    """The README's Method section: the app's Method text minus Limitations, links and Disclaimer."""
    for block in (METHOD_LIMITATIONS, METHOD_LINKS, "\n".join([METHOD_DISCLAIMER_HEADING, "", DISCLAIMER])):
        if f"\n\n{block}" not in app_method:
            raise ValueError(f"Block not found in the app's Method text: {block.splitlines()[0]}")
        app_method = app_method.replace(f"\n\n{block}", "")
    return f"{app_method}\n\n{README_ANSWER_KEY}"


# --- Sources --------------------------------------------------------------

SOURCES_HEADING = "Sources"
SOURCES_INTRO = "Every source URL in data/assumptions.csv, with the inputs it supports."
SOURCE_ITEM = "- [{site}]({url}): {inputs}"
