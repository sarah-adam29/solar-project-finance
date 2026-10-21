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
            "type": row["type"],
            "help": text.BASE_CASE.format(value=text.BASE_CASE_FORMATS[slider.parameter].format(base))
            + f"\n\n{text.INPUT_DEFINITIONS[slider.parameter]}"
            f"\n\n{source_text(rows, country, slider.parameter)}",
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
        "lcoe": results.lcoe_cents_per_kwh,
        "implied_rate": solve.implied_discount_rate(country, inputs=inputs),
        "project_irr": results.project_irr,
        "equity_irr": results.equity_irr,
        "min_dscr": results.min_dscr,
        "npv": results.project_npv / 1e6,
    }


# --- Tiles ----------------------------------------------------------------


@dataclass(frozen=True)
class Tile:
    key: str  # in ui_text.TILE_LABELS and the scenario results
    scale: float  # multiply the result by this before display
    decimals: int
    prefix: str = ""
    suffix: str = ""
    delta_unit: str = ""  # unit after the delta; defaults to the value's own
    higher_is_better: bool = True


TILES = {
    tile.key: tile
    for tile in [
        Tile("lcoe", 1, 2, higher_is_better=False),
        Tile("implied_rate", 100, 1, suffix="%", delta_unit=" pp"),
        Tile("npv", 1, 1, prefix="$", suffix="m"),
        Tile("project_irr", 100, 1, suffix="%", delta_unit=" pp"),
        Tile("equity_irr", 100, 1, suffix="%", delta_unit=" pp"),
        Tile("min_dscr", 1, 2, suffix="x"),
    ]
}


def signed(value: float, decimals: int, prefix: str = "", suffix: str = "", plus: bool = False) -> str:
    """A number with a true minus sign, e.g. −$210.8m or −6.3%."""
    value = round(value, decimals)
    sign = text.MINUS if value < 0 else ("+" if plus and value > 0 else "")
    return f"{sign}{prefix}{abs(value):,.{decimals}f}{suffix}"


def show_tile(tile: Tile, current: dict, base: dict) -> None:
    """One metric tile, with a delta only when the displayed value moved."""
    value, base_value = current[tile.key], base[tile.key]
    delta = arrow = colour = None
    if value is None:
        shown = text.NOT_MEANINGFUL
    else:
        shown = signed(value * tile.scale, tile.decimals, tile.prefix, tile.suffix)
    if value is not None and base_value is not None:
        # Compare the values as displayed, so a change too small to see shows no delta.
        difference = round(round(value * tile.scale, tile.decimals) - round(base_value * tile.scale, tile.decimals), tile.decimals)
        if difference != 0:
            unit = tile.delta_unit or tile.suffix
            delta = text.VERSUS_BASE.format(difference=signed(difference, tile.decimals, tile.prefix, unit, plus=True))
            arrow = "up" if difference > 0 else "down"
            colour = "green" if (difference > 0) == tile.higher_is_better else "red"
    help_text = text.OUTPUT_DEFINITIONS[tile.key]
    if value is None:
        help_text += f"\n\n{text.NOT_MEANINGFUL_REASONS.get(tile.key, text.NOT_MEANINGFUL)}"
    st.metric(
        text.TILE_LABELS[tile.key],
        shown,
        delta,
        delta_color=colour or "normal",
        delta_arrow=arrow or "auto",
        help=help_text,
    )


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

fixed = load_inputs(country)
st.caption(
    text.FIXED_ASSUMPTIONS.format(
        capacity=fixed.capacity, ppa_term=fixed.ppa_term, construction_years=fixed.construction_years
    ),
    help=text.FIXED_ASSUMPTIONS_HELP,
)

base = scenario(country, ())
current = scenario(country, tuple(sorted(overrides.items())))

# Top row: what the tariff covers. Bottom row: what investors and lenders get.
cost_tiles = st.columns(3)
with cost_tiles[0]:
    show_tile(TILES["lcoe"], current, base)
    st.caption(text.AWARDED_TARIFF.format(tariff=current["tariff_cents"]))
with cost_tiles[1]:
    show_tile(TILES["implied_rate"], current, base)
    discount_rate = settings["discount_rate"]
    st.caption(text.DISCOUNT_RATE_CAPTIONS[discount_rate["type"]].format(rate=discount_rate["base"]))
with cost_tiles[2]:
    show_tile(TILES["npv"], current, base)
    st.caption(text.NPV_DATE)

return_tiles = st.columns(3)
for column, key in zip(return_tiles, ("project_irr", "equity_irr", "min_dscr")):
    with column:
        show_tile(TILES[key], current, base)

with st.expander(text.GLOSSARY_TITLE):
    for heading, terms in (
        (text.GLOSSARY_INPUTS, text.INPUT_TERMS),
        (text.GLOSSARY_FIXED, text.FIXED_TERMS),
        (text.GLOSSARY_OUTPUTS, text.OUTPUT_TERMS),
    ):
        st.markdown(f"**{heading}**")
        st.markdown("\n".join(f"- **{term}**: {definition}" for term, _, definition in terms))
