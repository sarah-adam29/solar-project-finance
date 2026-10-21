"""Smoke tests: the Streamlit app runs for each country and shows what it should."""

import json
import sys
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

import ui_text as text

APP = str(Path(__file__).resolve().parent.parent / "app.py")
sys.path.insert(0, str(Path(__file__).resolve().parent))  # for importing test_answer_key
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
        base_case, definition, source = slider.help.split("\n\n")
        assert base_case.startswith("Base case: ")
        assert definition == text.INPUT_DEFINITIONS[slider.key]
        assert source.startswith("Source: ")


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


@pytest.mark.parametrize("country, ppa_term", [("KSA", 35), ("UAE", 30)])
def test_fixed_assumptions_follow_the_country(country, ppa_term):
    app = run_app(country)
    assert f"1,000 MWac plant · {ppa_term}-year PPA · 2-year build" in app.caption[0].value


def test_negative_numbers_use_a_true_minus_sign():
    app = run_app("KSA")
    values = {metric.label: metric.value for metric in app.metric}
    assert values[text.TILE_LABELS["equity_irr"]] == "\u22123.0%"
    assert "-" not in "".join(values.values())


def test_a_change_too_small_to_display_shows_no_delta():
    app = run_app("KSA")
    app.sidebar.slider(key="specific_yield_year1").set_value(2421.0).run()
    dscr = app.metric[list(text.TILE_LABELS).index("min_dscr")]
    assert dscr.value == "0.79x"
    assert not dscr.delta


def chart_specs(app: AppTest) -> list[dict]:
    return [json.loads(chart.proto.spec) for chart in app.get("plotly_chart")]


@pytest.mark.parametrize("country", ["KSA", "UAE"])
def test_three_charts_show_with_the_finding_first(country):
    app = run_app(country)
    assert len(chart_specs(app)) == 3
    finding_title = app.main.subheader[0].value
    assert finding_title.startswith("In this model, awarded tariffs only cover costs at about ")


@pytest.mark.parametrize("measure", ["lcoe", "equity_irr"])
def test_tornado_shows_the_top_five_drivers(measure):
    app = run_app("KSA")
    app.radio(key="tornado_measure").set_value(measure).run()
    tornado = chart_specs(app)[1]
    drivers = tornado["layout"]["yaxis"]["categoryarray"]
    assert len(drivers) == 5
    if measure == "lcoe":
        assert not {"Debt rate", "Gearing"} & set(drivers)
    assert any(caption.value.startswith("Top 5 of 8 drivers") for caption in app.main.caption)


def test_finding_chart_marks_the_two_scenarios():
    app = run_app("KSA")
    labels = [note["text"] for note in chart_specs(app)[0]["layout"]["annotations"]]
    assert any(label.startswith("Conflict +70bp: ") for label in labels)
    assert any(label.startswith("Severe +130bp: ") for label in labels)


@pytest.mark.parametrize("country", ["KSA", "UAE"])
def test_disclaimer_shows_in_full_under_the_title_and_in_the_footer(country):
    app = run_app(country)
    assert app.main.info[0].value == text.DISCLAIMER
    assert app.main.caption[-1].value == text.DISCLAIMER
    assert "[open an issue on GitHub](https://github.com/sarah-adam29/solar-project-finance/issues)" in text.DISCLAIMER
    assert "[message me on LinkedIn](https://www.linkedin.com/in/sarah-adam-a24949b1/)" in text.DISCLAIMER


def test_readme_carries_the_disclaimer_word_for_word():
    readme = (Path(APP).parent / "README.md").read_text()
    assert f"> [!IMPORTANT]\n> {text.DISCLAIMER}" in readme
    assert f"## Disclaimer and feedback\n{text.DISCLAIMER}" in readme


def test_trust_line_count_matches_the_answer_key_tests():
    import test_answer_key

    compared = [check for check in test_answer_key.CHECKS if test_answer_key.excel(check[0], check[1]) is not None]
    assert text.ANSWER_KEY_CHECKS == len(compared)
    app = run_app("KSA")
    expected = text.TRUST_LINE.format(checks=len(compared))
    assert any(caption.value == expected for caption in app.main.caption)


@pytest.mark.parametrize("country", ["KSA", "UAE"])
def test_detail_sections_show(country):
    app = run_app(country)
    labels = [expander.label for expander in app.expander]
    assert labels == [text.GLOSSARY_TITLE, text.CASH_FLOWS_TITLE, text.METHOD_TITLE]
    table = app.dataframe[0].value
    assert list(table.index) == [label for _, label, _ in text.CASH_FLOW_ROWS]
    assert list(table.columns[:3]) == ["Build 1", "Build 2", "Year 1"]
    assert len(app.get("download_button")) == 1
    method = app.expander[2].markdown[0].value
    assert text.DISCLAIMER in method
    assert "Debt tenor: " in method and "widened from" in method


def test_sources_list_each_csv_url_once():
    import pandas as pd

    from model.inputs import ASSUMPTIONS_CSV

    urls = pd.read_csv(ASSUMPTIONS_CSV)["source_url"].dropna().unique()
    app = run_app("KSA")
    sources = next(m.value for m in app.main.markdown if m.value.startswith("- ["))
    assert len(sources.splitlines()) == len(urls)
    assert all(f"]({url})" in sources for url in urls)


def test_no_emoji_in_app_text():
    import re

    emoji = re.compile("[\U0001F000-\U0001FAFF☀-➿️]")
    for path in ("app.py", "ui_text.py"):
        assert not emoji.search((Path(APP).parent / path).read_text()), path
