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
- Never put personal email addresses in any file.
- Every input in `data/assumptions.csv` has a `type`: public, derived,
  judgment or invented. Public and derived inputs must cite a reputable
  public source; judgment and invented inputs must be labelled as such in
  the app and README.
- Python results must match the Excel answer key within 0.1%, checked by tests.
- Use uv: `uv add` for packages, `uv run` to run code and tests.
- Small commits with plain-English messages.

## Units and conventions
- Currency: USD (SAR and AED are USD-pegged).
- Capex and O&M are per kWac; specific yield is per kWp (DC). Convert with
  the DC/AC ratio. Never mix the two.
- Cash flows, tariffs and discount rates are nominal. Tariffs are flat
  (not indexed) unless an input says otherwise.
- Discount rates are after tax.
- KSA tax: 20% income tax on the foreign-owned share of profit, 2.5% zakat
  on the Saudi/GCC share (input: `foreign_ownership_share`).
- UAE tax: 9% corporate tax on taxable income above AED 375,000.

## Key features (in build order)
1. Engine: inputs in, annual cash flows and metrics out (LCOE, project IRR,
   equity IRR, NPV, min and average DSCR).
2. KSA vs UAE side-by-side comparison from country presets.
3. Tornado chart on the five biggest drivers.
4. Solve for the tariff that hits a target equity IRR.
5. Back-solve the WACC implied by an awarded tender tariff.
6. Scenarios: base, conflict premium, severe (discount rate inputs).

## Data
- `data/assumptions.csv` – default inputs, ranges, type and source URL.
- `data/wacc/` – WACC Forecaster exports (credit the source in README).
- Do not commit IRENA reports or data files; cite table numbers and link.

## Planned structure
- `model/` – calculation engine
- `app.py` – Streamlit app
- `tests/` – pytest checks against the Excel answer key
- `excel/` – Excel answer key
- `data/` – assumptions and source data
