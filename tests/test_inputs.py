"""Checks on loading inputs from data/assumptions.csv."""

import pytest

from model.inputs import load_inputs


@pytest.mark.parametrize("country", ["KSA", "UAE"])
def test_project_life_must_equal_ppa_term(country):
    ppa_term = load_inputs(country).ppa_term
    with pytest.raises(ValueError, match="project_life .* must equal ppa_term"):
        load_inputs(country, {"project_life": ppa_term + 5})


def test_project_life_and_ppa_term_can_change_together():
    inputs = load_inputs("UAE", {"project_life": 25, "ppa_term": 25})
    assert inputs.project_life == inputs.ppa_term == 25
