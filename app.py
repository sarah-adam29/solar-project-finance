"""Streamlit calculator on top of the engine in model/.

Run locally with: uv run streamlit run app.py
All user-facing wording lives in ui_text.py.
"""

from dataclasses import dataclass, replace

import numpy as np
import pandas as pd
import plotly.graph_objects as go
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


# --- Charts ---------------------------------------------------------------

PLUM = "#58276B"
AMBER = "#C98A12"
INK = "#141B26"
GREY = "#9AA0A8"
GRID = "#ECE7EF"
BAND = "rgba(88, 39, 107, 0.10)"

FINDING_RATES = (0.02, 0.10)  # discount-rate range on the finding chart

# Multiply each tornado driver's input (model units) by this for its bar label.
TORNADO_INPUT_SCALES = {"Discount rate": 100, "Debt rate": 100, "Gearing": 100, "Degradation": 100}


def overrides_inputs(country: str, overrides: tuple):
    return load_inputs(country, dict(overrides))


@st.cache_data
def finding_curve(country: str, overrides: tuple, low: float, high: float) -> pd.DataFrame:
    """LCOE at each discount rate from low to high, other inputs as given."""
    inputs = overrides_inputs(country, overrides)
    rates = np.round(np.arange(low, high + 0.00001, 0.001), 6)
    lcoe = [run_model(replace(inputs, discount_rate=float(rate))).lcoe_cents_per_kwh for rate in rates]
    return pd.DataFrame({"rate": rates, "lcoe": lcoe})


@st.cache_data
def scenario_points(country: str, overrides: tuple) -> dict:
    """Discount rate, premium and LCOE for the conflict and severe scenarios."""
    inputs = overrides_inputs(country, overrides)
    lcoe = solve.discount_scenarios(country, inputs=inputs)
    premiums = {"conflict": inputs.conflict_premium, "severe": inputs.severe_premium}
    return {
        name: {"rate": inputs.discount_rate + premium, "bp": premium * 10000, "lcoe": lcoe[name]}
        for name, premium in premiums.items()
    }


@st.cache_data
def tornado_data(country: str, overrides: tuple) -> pd.DataFrame:
    return solve.sensitivities(country, inputs=overrides_inputs(country, overrides))


@st.cache_data
def required_tariffs(country: str, overrides: tuple) -> dict:
    """Tariff (US cents/kWh) for the equity IRR and DSCR targets, or None if unsolvable."""
    inputs = overrides_inputs(country, overrides)
    tariffs = {}
    for key, solver in (("equity_irr", solve.tariff_for_equity_irr), ("min_dscr", solve.tariff_for_min_dscr)):
        try:
            tariffs[key] = solver(country, inputs=inputs)
        except ValueError:
            tariffs[key] = None
    return tariffs


def percent_text(rate: float, decimals: int = 1) -> str:
    return signed(rate * 100, decimals, suffix="%")


def style(fig: go.Figure, height: int) -> go.Figure:
    """Theme colours and a layout that resizes with the page."""
    fig.update_layout(
        height=height,
        margin=dict(l=10, r=10, t=30, b=10),
        font=dict(family="sans-serif", color=INK, size=13),
        paper_bgcolor="white",
        plot_bgcolor="white",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
        hoverlabel=dict(bgcolor="white", font_color=INK),
    )
    fig.update_xaxes(gridcolor=GRID, zerolinecolor=GRID, linecolor=GRID, automargin=True)
    fig.update_yaxes(gridcolor=GRID, zerolinecolor=GRID, linecolor=GRID, automargin=True)
    return fig


def signed_ticks(low: float, high: float, scale: float, decimals: int, suffix: str = "") -> dict:
    """Axis ticks labelled with true minus signs (Plotly uses a hyphen)."""
    span = (high - low) * scale
    step = next(s for s in (0.05, 0.1, 0.2, 0.25, 0.5, 1, 2, 2.5, 5, 10, 20, 25, 50) if span / s <= 7)
    ticks = np.arange(np.floor(low * scale / step) * step, high * scale + step, step)
    ticks = [round(t, 6) for t in ticks if low * scale - 1e-6 <= t <= high * scale + 1e-6]
    return dict(
        tickvals=[t / scale for t in ticks],
        ticktext=[signed(t, decimals, suffix=suffix) for t in ticks],
    )


def finding_chart(country: str, overrides: tuple, current: dict, discount_rate: dict) -> tuple[str, go.Figure]:
    """Statement title and figure for the LCOE-versus-cost-of-capital chart."""
    implied, tariff = current["implied_rate"], current["tariff_cents"]
    band_low, band_high = discount_rate["low"] / 100, discount_rate["high"] / 100
    scenarios = scenario_points(country, overrides)
    # Widen the axis so the crossing and the scenario points are always on the chart.
    marks = [scenarios["severe"]["rate"]] + ([] if implied is None else [implied])
    low = min(FINDING_RATES[0], np.floor(min(marks) * 100 - 0.5) / 100)
    high = max(FINDING_RATES[1], np.ceil(max(marks) * 100 + 0.5) / 100)
    curve = finding_curve(country, overrides, low, high)

    tariff_changed = round(tariff, 2) != round(discount_rate["base_tariff"], 2)
    if implied is None:
        title = text.FINDING_TITLE_NO_CROSSING
    elif tariff_changed:
        title = text.FINDING_TITLE_CHANGED_TARIFF.format(tariff=tariff, rate=percent_text(implied, 0))
    else:
        title = text.FINDING_TITLE.format(rate=percent_text(implied, 0))

    fig = go.Figure()
    fig.add_vrect(x0=band_low, x1=band_high, fillcolor=BAND, line_width=0, layer="below")
    fig.add_annotation(
        x=(band_low + band_high) / 2, y=1, yref="paper", yanchor="bottom", showarrow=False,
        text=f"{text.FINDING_BAND[discount_rate['type']]}<br>"
        + text.FINDING_BAND_BASE.format(rate=percent_text(discount_rate["base"] / 100)),
        font=dict(color=PLUM, size=12),
    )
    fig.add_trace(go.Scatter(
        x=curve["rate"], y=curve["lcoe"], mode="lines", name=text.FINDING_LCOE_LINE,
        line=dict(color=PLUM, width=3),
        customdata=[(percent_text(r), signed(v, 2)) for r, v in zip(curve["rate"], curve["lcoe"])],
        hovertemplate=f"{text.FINDING_LCOE_LINE} %{{customdata[1]}} at %{{customdata[0]}}<extra></extra>",
    ))
    fig.add_hline(
        y=tariff, line=dict(color=INK, width=1.5, dash="dash"),
        annotation_text=(text.FINDING_TARIFF_LINE_CHANGED if tariff_changed else text.FINDING_TARIFF_LINE).format(tariff=tariff),
        annotation_position="bottom right", annotation_font_color=INK,
    )
    # Conflict label above the line and severe below it, each with a short pointer.
    placements = {"conflict": dict(ax=-20, ay=-34), "severe": dict(ax=20, ay=34)}
    for name, point in scenarios.items():
        fig.add_trace(go.Scatter(
            x=[point["rate"]], y=[point["lcoe"]], mode="markers", showlegend=False, hoverinfo="skip",
            marker=dict(color="white", size=10, line=dict(color=PLUM, width=2.5)),
        ))
        fig.add_annotation(
            x=point["rate"], y=point["lcoe"], showarrow=True, arrowcolor=INK, arrowwidth=1,
            arrowhead=0, standoff=6, **placements[name],
            font=dict(color=INK, size=12), bgcolor="rgba(255,255,255,0.85)",
            text=text.FINDING_SCENARIOS[name].format(bp=point["bp"], lcoe=signed(point["lcoe"], 2)),
        )
    if implied is not None:
        fig.add_trace(go.Scatter(
            x=[implied], y=[tariff], mode="markers", showlegend=False, hoverinfo="skip",
            marker=dict(color=PLUM, size=12, line=dict(color="white", width=2)),
        ))
        fig.add_annotation(
            x=implied, y=tariff, text=f"<b>{text.FINDING_CROSSING.format(rate=percent_text(implied))}</b>",
            showarrow=True, arrowcolor=PLUM, ax=30, ay=50, xanchor="left",
            font=dict(color=PLUM, size=13), bgcolor="white",
        )
    style(fig, 420)
    fig.update_layout(showlegend=False, margin=dict(t=50))
    # A little padding so Plotly keeps the end tick labels.
    fig.update_xaxes(title=text.FINDING_X_AXIS, range=[low - 0.002, high + 0.002], **signed_ticks(low, high, 100, 0, "%"))
    fig.update_yaxes(title=text.FINDING_Y_AXIS, rangemode="tozero")
    return title, fig


TORNADO_TOP = 5  # drivers shown, by swing


def tornado_chart(data: pd.DataFrame, measure: str, base_value: float, changed: bool) -> go.Figure:
    """Bars from the current value to the value with each input at its low and high end.

    Coloured by effect: plum improves the project, amber worsens it. For LCOE
    lower is better; for equity IRR higher is better.
    """
    lower_is_better = measure == "lcoe"
    scale, decimals = (1, 2) if measure == "lcoe" else (100, 1)
    suffix = "" if measure == "lcoe" else "%"

    rows = []
    for driver, row in data.iterrows():
        ends = []
        for side in ("low", "high"):
            value = row[f"{measure}_{side}"]
            if value is None or pd.isna(value):
                continue
            input_value = row[f"{side}_input"] * TORNADO_INPUT_SCALES.get(driver, 1)
            ends.append((value, text.TORNADO_INPUT_FORMATS[driver].format(input_value)))
        swing = max(v for v, _ in ends) - min(v for v, _ in ends) if ends else 0
        rows.append((text.TORNADO_DRIVERS[driver], ends, swing))
    # Keep the biggest swings for this measure; Plotly draws the first category at the bottom.
    rows = sorted(rows, key=lambda r: r[2], reverse=True)[:TORNADO_TOP][::-1]

    fig = go.Figure()
    for label, colour in ((text.TORNADO_IMPROVES, PLUM), (text.TORNADO_WORSENS, AMBER)):
        fig.add_trace(go.Bar(x=[None], y=[None], name=label, marker_color=colour, orientation="h", hoverinfo="skip"))
    for end in (0, 1):
        names, widths, colours, labels, hovers = [], [], [], [], []
        for name, ends, _ in rows:
            if len(ends) <= end:
                continue
            value, input_label = ends[end]
            difference = value - base_value
            improves = difference < 0 if lower_is_better else difference > 0
            names.append(name)
            widths.append(difference)
            colours.append(PLUM if improves else AMBER)
            labels.append(input_label if round(difference * scale, decimals) != 0 else "")
            hovers.append(f"{name} at {input_label}: {signed(value * scale, decimals, suffix=suffix)}")
        fig.add_trace(go.Bar(
            y=names, x=widths, base=base_value, orientation="h", showlegend=False,
            marker_color=colours, text=labels, textposition="outside", cliponaxis=False,
            textfont=dict(color=INK, size=12), hovertext=hovers, hoverinfo="text",
        ))

    ends = [base_value] + [v for _, e, _ in rows for v, _ in e]
    low, high = min(ends), max(ends)
    pad = (high - low) * 0.22 or 0.01
    style(fig, 130 + 42 * len(rows))
    fig.update_layout(barmode="overlay", bargap=0.35, margin=dict(t=40))
    fig.add_vline(x=base_value, line=dict(color=INK, width=1.5))
    fig.add_annotation(
        x=base_value, y=1, yref="paper", yanchor="bottom", showarrow=False, font=dict(color=INK, size=12),
        text=text.TORNADO_BASE_LINE["changed" if changed else "base"].format(
            value=signed(base_value * scale, decimals, suffix=suffix)),
    )
    fig.update_layout(legend=dict(y=-0.32, yanchor="top"), margin=dict(b=60))
    fig.update_xaxes(
        title=text.TORNADO_AXIS[measure], range=[low - pad, high + pad],
        **signed_ticks(low - pad, high + pad, scale, decimals if measure == "lcoe" else 0, suffix),
    )
    fig.update_yaxes(type="category", categoryorder="array", categoryarray=[r[0] for r in rows])
    return fig


def tariff_chart(current: dict, tariffs: dict, targets: dict, tariff_changed: bool) -> go.Figure:
    """Awarded tariff against the tariffs that would meet the investor and lender targets."""
    bars = [
        (text.TARIFF_BARS["tariff_changed" if tariff_changed else "tariff"], current["tariff_cents"], PLUM),
        (text.TARIFF_BARS["equity_irr"].format(target=targets["equity_irr"] * 100), tariffs["equity_irr"], GREY),
        (text.TARIFF_BARS["min_dscr"].format(target=targets["min_dscr"]), tariffs["min_dscr"], GREY),
    ]
    bars.reverse()  # first bar at the top
    values = [v or 0 for _, v, _ in bars]
    fig = go.Figure(go.Bar(
        y=[name for name, _, _ in bars], x=values, orientation="h",
        marker_color=[c for _, _, c in bars],
        text=[text.NOT_MEANINGFUL if v is None else signed(v, 2) for _, v, _ in bars],
        textposition="outside", cliponaxis=False, textfont=dict(color=INK, size=13),
        hoverinfo="skip",
    ))
    style(fig, 260)
    fig.update_layout(bargap=0.4, showlegend=False)
    fig.update_yaxes(type="category")
    fig.update_xaxes(title=text.FINDING_Y_AXIS, range=[0, max(values) * 1.2], rangemode="tozero")
    return fig


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

# --- Charts on the page ---------------------------------------------------

override_key = tuple(sorted(overrides.items()))
fixed_targets = {"equity_irr": fixed.target_equity_irr, "min_dscr": fixed.target_min_dscr}
tariff_changed = round(current["tariff_cents"], 2) != round(settings["ppa_tariff"]["base"], 2)
inputs_changed = any(settings[p]["base"] != st.session_state[p] for p in SLIDERS)
chart_config = {"displayModeBar": False, "responsive": True}

finding_title, finding_figure = finding_chart(
    country, override_key, current, {**settings["discount_rate"], "base_tariff": settings["ppa_tariff"]["base"]}
)
st.subheader(finding_title)
st.caption(text.FINDING_CAPTION)
st.plotly_chart(finding_figure, config=chart_config)
st.caption(text.FINDING_SCENARIO_NOTE.format(
    conflict=fixed.conflict_premium * 10000, severe=fixed.severe_premium * 10000))

tornado_column, tariff_column = st.columns(2, gap="large")
with tornado_column:
    st.subheader(text.TORNADO_TITLE)
    measure = st.radio(
        text.TORNADO_MEASURE_LABEL, list(text.TORNADO_MEASURES), key="tornado_measure",
        format_func=text.TORNADO_MEASURES.get, horizontal=True,
    )
    st.caption(text.TORNADO_CAPTION.format(measure=text.TORNADO_MEASURES[measure]))
    if current[measure] is None:
        st.info(text.TORNADO_NO_BASE)
    else:
        drivers = tornado_data(country, override_key)
        st.plotly_chart(tornado_chart(drivers, measure, current[measure], inputs_changed), config=chart_config)
        st.caption(text.TORNADO_TOP_NOTE.format(shown=min(TORNADO_TOP, len(drivers)), total=len(drivers)))
with tariff_column:
    st.subheader(text.TARIFF_TITLE)
    st.caption(text.TARIFF_CAPTION)
    st.plotly_chart(
        tariff_chart(current, required_tariffs(country, override_key), fixed_targets, tariff_changed),
        config=chart_config,
    )
