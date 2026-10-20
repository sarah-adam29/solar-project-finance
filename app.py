"""Streamlit calculator on top of the engine in model/.

Run locally with: uv run streamlit run app.py
"""

from dataclasses import dataclass

import pandas as pd
import streamlit as st

from model import solve
from model.engine import run_model
from model.inputs import ASSUMPTIONS_CSV, COUNTRIES, load_inputs

st.set_page_config(
    page_title="Gulf solar tariffs and the cost of capital",
    layout="wide",
)


# --- Sliders -------------------------------------------------------------


@dataclass(frozen=True)
class Slider:
    parameter: str  # name in data/assumptions.csv and in Inputs
    label: str
    step: float
    format: str
    to_model: float  # multiply the slider value by this to get model units


SLIDERS = [
    Slider("ppa_tariff", "PPA tariff (US cents/kWh)", 0.01, "%.2f", 0.01),
    Slider("capex", "Capex (USD/kWac)", 5.0, "%.0f", 1),
    Slider("fixed_om", "Fixed O&M (USD/kWac per year)", 0.5, "%.1f", 1),
    Slider("specific_yield_year1", "Specific yield, year 1 (kWh/kWp)", 1.0, "%.0f", 1),
    Slider("discount_rate", "Discount rate (%)", 0.1, "%.1f", 0.01),
    Slider("debt_rate", "Debt rate (%)", 0.1, "%.1f", 0.01),
    Slider("gearing", "Gearing (% debt)", 1.0, "%.0f", 0.01),
    Slider("debt_tenor", "Debt tenor (years)", 1, "%d", 1),
    Slider("degradation", "Degradation (% per year)", 0.05, "%.2f", 0.01),
    Slider("dc_ac_ratio", "DC/AC ratio", 0.01, "%.2f", 1),
]

TYPE_LABELS = {
    "public": "Public source",
    "derived": "Derived from public sources",
    "judgment": "Judgment",
    "invented": "Invented",
}


@st.cache_data
def slider_settings(country: str) -> dict[str, dict]:
    """Base, slider range and help text for each slider, from the CSV."""
    table = pd.read_csv(ASSUMPTIONS_CSV)
    rows = table[table["country"] == country].set_index("parameter")
    settings = {}
    for slider in SLIDERS:
        row = rows.loc[slider.parameter]
        base, low, high = row["base"], row["low"], row["high"]
        # Widen a one-sided range by mirroring the other side, so the slider
        # can move both ways from the base case.
        if low == base:
            low = round(base - (high - base), 6)
        if high == base:
            high = round(base + (base - low), 6)
        if slider.step == 1 and slider.format == "%d":
            base, low, high = int(base), int(low), int(high)
        else:
            base, low, high = float(base), float(low), float(high)
        settings[slider.parameter] = {
            "base": base,
            "low": low,
            "high": high,
            "help": f"{TYPE_LABELS.get(row['type'], row['type'])}: {row['basis']}",
        }
    return settings


def reset_to_base() -> None:
    """Put every slider back to the selected country's base case."""
    settings = slider_settings(st.session_state["country"])
    for slider in SLIDERS:
        st.session_state[slider.parameter] = settings[slider.parameter]["base"]


# --- Cached engine runs ---------------------------------------------------


@st.cache_data
def scenario(country: str, overrides: tuple) -> dict:
    """Headline metrics for one set of inputs."""
    inputs = load_inputs(country, dict(overrides))
    results = run_model(inputs)
    return {
        "tariff_cents": inputs.ppa_tariff * 100,
        "lcoe_cents": results.lcoe_cents_per_kwh,
        "implied_rate": solve.implied_discount_rate(country, inputs=inputs),
        "project_irr": results.project_irr,
        "equity_irr": results.equity_irr,
        "min_dscr": results.min_dscr,
    }


# --- Formatting -----------------------------------------------------------


def percent(value: float | None) -> str:
    return "n.m." if value is None else f"{value:.1%}"


def change(current: float | None, base: float | None, unit: str, scale: float = 1, decimals: int = 2):
    """Delta text for a tile, or None when unchanged or not meaningful."""
    if current is None or base is None:
        return None
    difference = (current - base) * scale
    if round(difference, decimals) == 0:
        return None
    return f"{difference:+.{decimals}f}{unit} vs base"


# --- Page -----------------------------------------------------------------

st.title("What do Gulf solar tariffs imply about the cost of capital?")
st.write(
    "A project finance model of utility-scale solar in Saudi Arabia and the UAE, "
    "built from public data and checked against a hand-built Excel model."
)

with st.sidebar:
    if "country" not in st.session_state:
        st.session_state["country"] = COUNTRIES[0]
        reset_to_base()
    country = st.radio("Country", COUNTRIES, key="country", horizontal=True, on_change=reset_to_base)

    settings = slider_settings(country)
    overrides = {}
    for slider in SLIDERS:
        setting = settings[slider.parameter]
        value = st.slider(
            slider.label,
            min_value=setting["low"],
            max_value=setting["high"],
            step=slider.step,
            format=slider.format,
            help=setting["help"],
            key=slider.parameter,
        )
        overrides[slider.parameter] = value * slider.to_model

    st.button("Reset to base case", on_click=reset_to_base)
    st.caption("Ranges from public sources; see Method below.")

base = scenario(country, ())
current = scenario(country, tuple(sorted(overrides.items())))

tiles = st.columns(5)
with tiles[0]:
    st.metric(
        "LCOE (US cents/kWh)",
        f"{current['lcoe_cents']:.2f}",
        change(current["lcoe_cents"], base["lcoe_cents"], ""),
        delta_color="inverse",
        help="Levelised cost of electricity: discounted capex and O&M over discounted generation.",
    )
    st.caption(f"Awarded tariff: {current['tariff_cents']:.2f} US cents/kWh")
with tiles[1]:
    st.metric(
        "Implied cost of capital",
        percent(current["implied_rate"]),
        change(current["implied_rate"], base["implied_rate"], " pp", 100, 1),
        help="The discount rate at which LCOE equals the tariff.",
    )
with tiles[2]:
    st.metric(
        "Project IRR",
        percent(current["project_irr"]),
        change(current["project_irr"], base["project_irr"], " pp", 100, 1),
        help="the project never pays back" if current["project_irr"] is None else "Unlevered, after tax.",
    )
with tiles[3]:
    st.metric(
        "Equity IRR",
        percent(current["equity_irr"]),
        change(current["equity_irr"], base["equity_irr"], " pp", 100, 1),
        help="equity is never paid back" if current["equity_irr"] is None else "Return to shareholders after debt service and tax.",
    )
with tiles[4]:
    st.metric(
        "Minimum DSCR",
        f"{current['min_dscr']:.2f}x",
        change(current["min_dscr"], base["min_dscr"], "x"),
        help="Lowest yearly cash available for debt service divided by debt service.",
    )
