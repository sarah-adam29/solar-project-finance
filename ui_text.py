"""All user-facing text in the Streamlit app, so wording can be edited in one place."""

# --- Page -----------------------------------------------------------------

PAGE_TITLE = "Gulf solar tariffs and the cost of capital"
TITLE = "What do Gulf solar tariffs imply about the cost of capital?"
INTRO = (
    "A project finance model of utility-scale solar in Saudi Arabia and the UAE, "
    "built from public data and checked against a hand-built Excel model."
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
RANGES_NOTE = "Ranges from public sources; see Method below."

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

GLOSSARY_TITLE = "What the terms mean"
GLOSSARY_INPUTS = "Inputs"
GLOSSARY_FIXED = "Fixed in this model"
GLOSSARY_OUTPUTS = "Outputs"

# --- Charts ---------------------------------------------------------------

# The finding: LCOE across discount rates against the tariff.
FINDING_TITLE = "Awarded tariffs only cover costs at about {rate}"
FINDING_TITLE_CHANGED_TARIFF = "A {tariff:.2f}-cent tariff covers costs at about {rate}"
FINDING_TITLE_NO_CROSSING = "The tariff and the LCOE line don't cross at any cost of capital the model can test"
FINDING_CAPTION = (
    "The line is the LCOE at each cost of capital, with every other input as set in the sidebar. "
    "Where it crosses the tariff is the return the tariff actually pays for."
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
# Shaded discount-rate range from the CSV, by the type of the country's base rate.
FINDING_BAND = {
    "public": "Published estimates",
    "judgment": "Estimates (judgment)",
}
FINDING_BAND_BASE = "base {rate}"

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
    "Specific yield": "Specific yield",
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
    "Specific yield": "{:,.0f} kWh/kWp",
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
    "equity_irr": "For a {target:.0f}% equity IRR",
    "min_dscr": "For a {target:.2f}× minimum DSCR",
}
