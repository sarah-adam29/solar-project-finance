# Solar Project Finance

> Work in progress: this README is a skeleton. Sections marked _To do_ will be
> filled in as the model is built.

## Overview
A project finance model for utility-scale solar PV in Saudi Arabia (KSA) and
the United Arab Emirates (UAE), delivered as a Streamlit web app. It takes a
set of project inputs and produces annual cash flows and the headline metrics:
LCOE, project IRR, equity IRR, NPV, and minimum and average DSCR.

This is a public portfolio project. It uses public sources and invented inputs
only.

## Key questions
- What does solar power cost to produce in KSA and the UAE, and what drives
  the difference between the two?
- Which five inputs move the result the most?
- What tariff does a project need to reach a target equity IRR?
- What cost of capital (WACC) is implied by an awarded tender tariff?
- How do the results change under higher discount rate scenarios (base,
  conflict premium, severe)?

## Method
_To do._ Describe how the engine turns inputs into annual cash flows and
metrics, and how the Python results are checked against the Excel answer key
in `excel/` (they must match within 0.1%).

Conventions:
- Currency is USD (SAR and AED are pegged to the USD).
- Capex and O&M are per kWac; specific yield is per kWp (DC). The DC/AC ratio
  converts between the two.
- Cash flows, tariffs and discount rates are nominal. Tariffs are flat unless
  an input says otherwise.
- Discount rates are after tax.

## Assumptions
Default inputs, their ranges, type and source are listed in
[data/assumptions.csv](data/assumptions.csv).

Every input has a type:

| Type | Meaning |
| --- | --- |
| public | Taken directly from a cited public source |
| derived | Calculated from cited public sources |
| judgment | The author's own estimate, labelled as such |
| invented | Illustrative placeholder, labelled as such |

## How to run
This project uses [uv](https://docs.astral.sh/uv/).

```bash
uv sync                        # install dependencies
uv run streamlit run app.py    # start the web app
uv run pytest                  # check results against the Excel answer key
```

_To do:_ the app and tests are not built yet.

## Limitations
_To do._ List what the model simplifies or leaves out.

## Sources
- Hatton, L., Staffell, I., Jansen, M., Oluleye, G., & Hawkes, A. (2026).
  *Historical and future projected costs of capital for ten energy
  technologies across 176 countries* [Dataset]. Zenodo.
  https://doi.org/10.5281/zenodo.18662192 — licensed CC BY 4.0.
  Used for: discount-rate defaults (`data/wacc/WACC_ESTIMATES_WIDE.csv`).

- IRENA (2026), *Renewable power generation costs in 2025*, International
  Renewable Energy Agency, Abu Dhabi. ISBN 978-92-9260-749-4.
  https://www.irena.org/-/media/Files/IRENA/Agency/Publication/2026/Jul/IRENA_TEC_RPGC_in_2025_2026.pdf
  © IRENA 2026; used with acknowledgement per IRENA's terms.
  Used for: O&M default (Table A4), capex upper bound (Fig 3.2),
  real WACC cross-check (Table A2), LCOE comparison (Fig 3.7).

## Licence
MIT. See [LICENSE](LICENSE).
