"""All user-facing text in the Streamlit app, so wording can be edited in one place."""

# --- Page -----------------------------------------------------------------

PAGE_TITLE = "Gulf solar tariffs and the cost of capital"
TITLE = "What do Gulf solar tariffs imply about the cost of capital?"
INTRO = (
    "A project finance model of utility-scale solar in Saudi Arabia and the UAE, "
    "built from public data and checked against a hand-built Excel model."
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

TILE_LABELS = {
    "lcoe": "LCOE (US cents/kWh)",
    "implied_rate": "Implied cost of capital",
    "project_irr": "Project IRR",
    "equity_irr": "Equity IRR",
    "min_dscr": "Minimum DSCR",
    "npv": "Project NPV (USD m)",
}
AWARDED_TARIFF = "Awarded tariff: {tariff:.2f} US cents/kWh"
NOT_MEANINGFUL = "n.m."
NOT_MEANINGFUL_REASONS = {
    "project_irr": "n.m.: the project never pays back.",
    "equity_irr": "n.m.: equity is never paid back.",
}
NPV_DATE = "At financial close, start of construction"
NPV_BASIS = (
    "Valued at financial close, with each year's cash flow at the end of that year. Nominal USD, "
    "after tax, before debt, for a 1,000 MW plant (an invented reference size; NPV scales with it)."
)
VERSUS_BASE = "{difference} vs base"

GLOSSARY_TITLE = "What the terms mean"
GLOSSARY_INPUTS = "Inputs"
GLOSSARY_OUTPUTS = "Outputs"
