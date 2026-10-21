"""Streamlit calculator on top of the engine in model/.

Run locally with: uv run streamlit run app.py
All user-facing wording lives in ui_text.py.
"""

from dataclasses import dataclass

import pandas as pd
import streamlit as st

import ui_text as text
from model import solve
from model.engine import run_model
from model.inputs import ASSUMPTIONS_CSV, COUNTRIES, load_inputs

st.set_page_config(page_title=text.PAGE_TITLE, layout="wide")


# --- Sliders -------------------------------------------------------------


@dataclass(frozen=True)
class Slider:
    parameter: str  # name in data/assumptions.csv and in Inputs
    step: float
    format: str
    to_model: float  # multiply the slider value by this to get model units


SLIDERS = {
    slider.parameter: slider
    for slider in [
        Slider("ppa_tariff", 0.01, "%.2f", 0.01),
        Slider("capex", 5.0, "%.0f", 1),
        Slider("fixed_om", 0.5, "%.1f", 1),
        Slider("specific_yield_year1", 1.0, "%.0f", 1),
        Slider("degradation", 0.05, "%.2f", 0.01),
        Slider("dc_ac_ratio", 0.01, "%.2f", 1),
        Slider("gearing", 1.0, "%.0f", 0.01),
        Slider("debt_rate", 0.1, "%.1f", 0.01),
        Slider("debt_tenor", 1, "%d", 1),
        Slider("discount_rate", 0.1, "%.1f", 0.01),
    ]
}


def source_text(rows: pd.DataFrame, country: str, parameter: str) -> str:
    """The CSV basis for one input, with its type, ready for a tooltip."""
    row = rows.loc[(country, parameter)]
    basis = row["basis"]
    # UAE rows that say "Same as KSA" get the KSA wording in full.
    for prefix in ("Same basis as KSA", "Same as KSA"):
        if basis.startswith(prefix):
            basis = rows.loc[("KSA", parameter), "basis"] + basis[len(prefix):]
            break
    label = text.TYPE_LABELS.get(row["type"], row["type"])
    # A single ~ is strikethrough in Streamlit markdown.
    return f"Source: {basis} ({label})".replace("~", r"\~")


@st.cache_data
def slider_settings(country: str) -> dict[str, dict]:
    """Base, slider range and help text for each slider, from the CSV."""
    rows = pd.read_csv(ASSUMPTIONS_CSV).set_index(["country", "parameter"])
    settings = {}
    for slider in SLIDERS.values():
        row = rows.loc[(country, slider.parameter)]
        base, low, high = row["base"], row["low"], row["high"]
        # Widen a one-sided range by mirroring the other side, so the slider
        # can move both ways from the base case.
        if low == base:
            low = round(base - (high - base), 6)
        if high == base:
            high = round(base + (base - low), 6)
        if slider.format == "%d":
            base, low, high = int(base), int(low), int(high)
        else:
            base, low, high = float(base), float(low), float(high)
        settings[slider.parameter] = {
            "base": base,
            "low": low,
            "high": high,
            "help": f"{text.INPUT_DEFINITIONS[slider.parameter]}\n\n"
            f"{source_text(rows, country, slider.parameter)}",
        }
    return settings


def reset_to_base() -> None:
    """Put every slider back to the selected country's base case."""
    settings = slider_settings(st.session_state["country"])
    for parameter in SLIDERS:
        st.session_state[parameter] = settings[parameter]["base"]


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
        "npv_millions": results.project_npv / 1e6,
    }


# --- Formatting -----------------------------------------------------------


def percent(value: float | None) -> str:
    return text.NOT_MEANINGFUL if value is None else f"{value:.1%}"


def change(current: float | None, base: float | None, unit: str, scale: float = 1, decimals: int = 2):
    """Delta text for a tile, or None when unchanged or not meaningful."""
    if current is None or base is None:
        return None
    difference = (current - base) * scale
    if round(difference, decimals) == 0:
        return None
    return text.VERSUS_BASE.format(difference=f"{difference:+.{decimals}f}{unit}")


def millions(value: float) -> str:
    """USD millions for display, e.g. −$210.8m."""
    sign = "−" if round(value, 1) < 0 else ""
    return f"{sign}${abs(value):,.1f}m"


def money_change(current: float, base: float):
    """Delta text in USD millions. Kept to a plain +/- sign so Streamlit
    reads the direction: higher NPV is better, so up shows green."""
    difference = current - base
    if round(difference, 1) == 0:
        return None
    sign = "+" if difference > 0 else "-"
    return text.VERSUS_BASE.format(difference=f"{sign}${abs(difference):,.1f}m")


def tile_help(key: str, value: float | None = 0.0) -> str:
    """Tooltip for a tile: the definition, plus why the value is n.m. if it is."""
    help_text = text.OUTPUT_DEFINITIONS[key]
    if value is None:
        help_text += f"\n\n{text.NOT_MEANINGFUL_REASONS[key]}"
    return help_text


# --- Page -----------------------------------------------------------------

st.title(text.TITLE)
st.write(text.INTRO)

with st.sidebar:
    if "country" not in st.session_state:
        st.session_state["country"] = COUNTRIES[0]
        reset_to_base()
    country = st.radio(text.COUNTRY_LABEL, COUNTRIES, key="country", horizontal=True, on_change=reset_to_base)

    settings = slider_settings(country)
    overrides = {}
    for header, caption, parameters in text.GROUPS:
        st.subheader(header)
        st.caption(caption)
        for parameter in parameters:
            slider, setting = SLIDERS[parameter], settings[parameter]
            value = st.slider(
                text.SLIDER_LABELS[parameter],
                min_value=setting["low"],
                max_value=setting["high"],
                step=slider.step,
                format=slider.format,
                help=setting["help"],
                key=parameter,
            )
            overrides[parameter] = value * slider.to_model

    st.button(text.RESET_BUTTON, on_click=reset_to_base)
    st.caption(text.RANGES_NOTE)

base = scenario(country, ())
current = scenario(country, tuple(sorted(overrides.items())))

# Top row: what the tariff covers. Bottom row: what investors and lenders get.
cost_tiles = st.columns(3)
with cost_tiles[0]:
    st.metric(
        text.TILE_LABELS["lcoe"],
        f"{current['lcoe_cents']:.2f}",
        change(current["lcoe_cents"], base["lcoe_cents"], ""),
        delta_color="inverse",
        help=tile_help("lcoe"),
    )
    st.caption(text.AWARDED_TARIFF.format(tariff=current["tariff_cents"]))
with cost_tiles[1]:
    st.metric(
        text.TILE_LABELS["implied_rate"],
        percent(current["implied_rate"]),
        change(current["implied_rate"], base["implied_rate"], " pp", 100, 1),
        help=tile_help("implied_rate"),
    )
with cost_tiles[2]:
    st.metric(
        text.TILE_LABELS["npv"],
        millions(current["npv_millions"]),
        money_change(current["npv_millions"], base["npv_millions"]),
        help=tile_help("npv"),
    )
    st.caption(text.NPV_DATE)

return_tiles = st.columns(3)
with return_tiles[0]:
    st.metric(
        text.TILE_LABELS["project_irr"],
        percent(current["project_irr"]),
        change(current["project_irr"], base["project_irr"], " pp", 100, 1),
        help=tile_help("project_irr", current["project_irr"]),
    )
with return_tiles[1]:
    st.metric(
        text.TILE_LABELS["equity_irr"],
        percent(current["equity_irr"]),
        change(current["equity_irr"], base["equity_irr"], " pp", 100, 1),
        help=tile_help("equity_irr", current["equity_irr"]),
    )
with return_tiles[2]:
    st.metric(
        text.TILE_LABELS["min_dscr"],
        f"{current['min_dscr']:.2f}x",
        change(current["min_dscr"], base["min_dscr"], "x"),
        help=tile_help("min_dscr"),
    )

with st.expander(text.GLOSSARY_TITLE):
    for heading, terms in ((text.GLOSSARY_INPUTS, text.INPUT_TERMS), (text.GLOSSARY_OUTPUTS, text.OUTPUT_TERMS)):
        st.markdown(f"**{heading}**")
        st.markdown("\n".join(f"- **{term}**: {definition}" for term, _, definition in terms))
