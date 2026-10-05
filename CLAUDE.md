# Solar Project Finance

## Purpose
Public portfolio project: a project finance model for utility-scale solar PV
in KSA and the UAE (LCOE, project and equity IRR, NPV, DSCR, sensitivities),
delivered as a Streamlit web app.

## About me
Strategy consultant with strong Excel and finance skills, newer to Python.
Explain what you are doing in plain English. Prefer simple, readable code
over clever code.

## Rules
- Public repo: never add confidential or identifiable information (client
  names, engagement data, employer materials). Public sources and invented
  inputs only.
- Every default assumption must cite a reputable public source.
- Python results must match the Excel answer key within 0.1%, checked by tests.
- Use uv: `uv add` for packages, `uv run` to run code and tests.
- Small commits with plain-English messages.

## Planned structure
- `model/` – calculation engine: inputs in, cash flows and metrics out
- `app.py` – Streamlit app
- `tests/` – pytest checks against the Excel answer key
- `excel/` – Excel answer key
- `data/assumptions.csv` – default inputs with sources
