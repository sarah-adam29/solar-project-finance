"""Smoke test: the Streamlit app runs for each country and shows its tiles."""

from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

import ui_text as text

APP = str(Path(__file__).resolve().parent.parent / "app.py")
SIDEBAR_ORDER = [parameter for _, _, parameters in text.GROUPS for parameter in parameters]


def run_app(country: str) -> AppTest:
    app = AppTest.from_file(APP, default_timeout=60).run()
    if country != app.sidebar.radio[0].value:
        app.sidebar.radio[0].set_value(country).run()
    return app


@pytest.mark.parametrize("country", ["KSA", "UAE"])
def test_app_runs_and_shows_tiles(country):
    app = run_app(country)
    assert not app.exception
    assert app.sidebar.radio[0].value == country
    assert [metric.label for metric in app.metric] == list(text.TILE_LABELS.values())
    assert all(metric.help for metric in app.metric)


def test_sidebar_is_grouped_with_help_text():
    app = run_app("KSA")
    assert [header.value for header in app.sidebar.subheader] == [header for header, _, _ in text.GROUPS]
    assert [slider.label for slider in app.sidebar.slider] == [text.SLIDER_LABELS[p] for p in SIDEBAR_ORDER]
    for slider in app.sidebar.slider:
        assert slider.help.startswith(text.INPUT_DEFINITIONS[slider.key])
        assert "\n\nSource: " in slider.help


def test_moving_a_slider_shows_a_change_and_reset_restores_base():
    app = run_app("UAE")
    base_lcoe = app.metric[0].value
    app.sidebar.slider(key="capex").set_value(450.0).run()
    assert not app.exception
    assert app.metric[0].value != base_lcoe
    assert app.metric[0].delta is not None
    app.sidebar.button[0].click().run()
    assert app.metric[0].value == base_lcoe


def test_npv_is_in_usd_millions_and_a_higher_npv_shows_green():
    app = run_app("UAE")
    npv = app.metric[list(text.TILE_LABELS).index("npv")]
    assert npv.value == "−$210.8m"
    assert npv.help == text.OUTPUT_DEFINITIONS["npv"]
    app.sidebar.slider(key="ppa_tariff").set_value(1.60).run()
    npv = app.metric[list(text.TILE_LABELS).index("npv")]
    assert npv.delta.startswith("+$")
    assert (npv.proto.direction, npv.proto.color) == (npv.proto.UP, npv.proto.GREEN)
