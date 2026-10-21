# Solar Project Finance

> [!IMPORTANT]
> Personal learning project, not investment advice. I built this model myself from public sources to learn project finance modelling and Python. It has not been reviewed or validated by industry experts, developers, lenders or other market participants, and its results may be wrong. Please don't use it for investment, lending or policy decisions. If you have better data or spot an error, I'd be glad to hear from you: [open an issue on GitHub](https://github.com/sarah-adam29/solar-project-finance/issues) or [message me on LinkedIn](https://www.linkedin.com/in/sarah-adam-a24949b1/).

> Work in progress: this README is a skeleton. Sections marked _To do_ will be
> filled in as the model is built.

Live app: [link to be added]

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
**How the model works**

- **Timeline.** Annual periods. Period 1 is financial close, when the loans are signed and construction starts. Construction takes 2 years, with 40% of capex spent in the first year and 60% in the second. The plant then runs for the PPA term: KSA 35 years, UAE 30 years.
- **Funding.** During construction, capex is paid by debt and equity in proportion to the gearing. Interest during construction is added to the loan.
- **Debt.** The loan is repaid as an annuity (equal yearly payments of interest plus principal) over the debt tenor. The payment is worked out once, on the balance at the commercial operation date (COD).
- **Revenue and costs.** Generation is plant size × DC/AC ratio × specific yield, falling each year by the degradation rate. Revenue is generation × tariff. The tariff and O&M are flat in nominal terms.
- **Tax.** KSA: 20% income tax on the foreign-owned share of taxable profit and 2.5% zakat on the Saudi share (v1 applies zakat to profit). UAE: 9% corporate tax on taxable income above AED 375,000. Depreciation is straight-line over the project life, on capex plus capitalised interest.
- **LCOE.** Discounted capex plus discounted O&M, divided by discounted generation, at the discount rate. It excludes tax and financing structure.
- **Returns.** Project IRR uses cash flows after tax and before debt, with tax worked out as if there were no debt. Equity IRR uses cash flows to shareholders after debt service and tax. NPV discounts project cash flows to financial close, with each year's cash flow at the end of that year.
- **Solve-fors.** The implied cost of capital is the discount rate at which the LCOE equals the tariff. The tariffs for the equity IRR and DSCR targets are found the same way, by searching for the value that hits the target.
- **Sensitivities and scenarios.** The tornado moves one input at a time to the low and high end of its source range, with everything else as set in the sidebar. The conflict and severe scenarios add 70bp and 130bp to the discount rate.
- **Checks.** The Python engine is tested against a hand-built Excel model: 92 values must match within 0.1%.

**Fixed in this model**

The plant size (1,000 MWac) is an invented reference size so the two countries compare like for like. Costs and output are per kW, so it doesn't change LCOE, IRRs or DSCR; it only scales NPV and the cash-flow table.

**Judgment and invented inputs**

Every input in data/assumptions.csv is labelled public, derived, judgment or invented. These are the author's own judgment or invented:

- Plant size (KSA and UAE): invented
- DC/AC ratio (KSA and UAE): judgment
- Capex (KSA and UAE): judgment
- Debt tenor (KSA and UAE): judgment
- Debt rate (KSA and UAE): judgment
- Foreign ownership share (KSA): invented
- Discount rate (UAE): judgment
- Project life (KSA and UAE): judgment
- Construction period (KSA and UAE): judgment
- Capex spent in build year 1 (KSA and UAE): judgment
- Capex spent in build year 2 (KSA and UAE): judgment
- Target equity IRR (KSA and UAE): judgment
- Target minimum DSCR (KSA and UAE): judgment
- Conflict premium (KSA and UAE): judgment
- Severe premium (KSA and UAE): judgment

**Slider ranges**

Each slider runs from the low to the high value in data/assumptions.csv. Where the source range starts or ends at the base case, the slider is widened by mirroring the other side, so it can move both ways from the base case:

- KSA Degradation: low end widened from 0.5 to 0.3 %/yr
- KSA Debt tenor: low end widened from 30 to 28 years
- UAE Degradation: low end widened from 0.5 to 0.3 %/yr
- UAE Debt tenor: high end widened from 27 to 29 years

**Limitations (v1)**

- Flat tariff and O&M.
- All capacity reaches COD together (no phased COD).
- Pro-rata debt/equity funding during construction.
- Interest during construction capitalised into debt.
- No DSRA.
- No tax-loss carry-forward.
- Zakat approximated as 2.5% of profit.
- Construction period fixed at 2 years.

**Code and answer key**

- [GitHub repository](https://github.com/sarah-adam29/solar-project-finance)
- [Excel answer key](https://github.com/sarah-adam29/solar-project-finance/blob/main/excel/solar_answer_key.xlsx)

**Disclaimer**

Personal learning project, not investment advice. I built this model myself from public sources to learn project finance modelling and Python. It has not been reviewed or validated by industry experts, developers, lenders or other market participants, and its results may be wrong. Please don't use it for investment, lending or policy decisions. If you have better data or spot an error, I'd be glad to hear from you: [open an issue on GitHub](https://github.com/sarah-adam29/solar-project-finance/issues) or [message me on LinkedIn](https://www.linkedin.com/in/sarah-adam-a24949b1/).

**Conventions**

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
uv run python -m model         # print a KSA and UAE summary
uv run pytest                  # check results against the Excel answer key
```

`uv run pytest` compares the Python results with the values saved in
`excel/solar_answer_key.xlsx` and prints a cell-by-cell table. Every value must
match within 0.1%. It also runs smoke tests on the app.

To use the engine from Python:

```python
from model.inputs import load_inputs
from model.engine import run_model
from model import solve

results = run_model(load_inputs("KSA"))           # base case from data/assumptions.csv
results.lcoe_cents_per_kwh, results.equity_irr    # headline metrics
results.table                                     # annual cash flows, one row per year

run_model(load_inputs("UAE", {"capex": 450}))     # override inputs, in model units
solve.tariff_for_equity_irr("KSA")                # tariff (US cents/kWh) for the target equity IRR
solve.sensitivities("UAE")                        # LCOE and equity IRR at each input's low and high
```

The engine is in `model/`: `inputs.py` loads and converts the inputs,
`engine.py` builds the annual cash flows and metrics, and `solve.py` holds the
solve-fors, discount-rate scenarios and sensitivities.

### Run the app locally

```bash
uv sync
uv run streamlit run app.py
```

Streamlit prints a local URL, usually http://localhost:8501. All the wording in
the app lives in `ui_text.py`, so it can be edited in one place.

`requirements.txt` is what Streamlit Community Cloud installs. Re-export it
whenever dependencies change:

```bash
uv export --no-dev --no-hashes --format requirements-txt > requirements.txt
```

## What drives the answer
In this model, the base-case LCOE is 1.94 US cents/kWh in KSA and 2.12 in the
UAE, against awarded tariffs of 1.30 and 1.41. The app's tornado moves one input
at a time across its source range, with everything else at the base case:

- **LCOE.** Capex moves it most (KSA 1.66 to 2.45, UAE 1.81 to 2.67 US
  cents/kWh, for capex of $450 to $725/kW), then fixed O&M, the discount rate,
  specific yield and the DC/AC ratio. Debt rate and gearing don't affect LCOE.
- **No single input closes the gap.** In this model, the most favourable end of
  any one range still leaves the LCOE above the awarded tariff: the lowest is
  1.66 in KSA and 1.81 in the UAE, both with capex at $450/kW.
- **Equity IRR.** Fixed O&M swings it most, because its upper end ($27/kW/yr, a
  US benchmark) is far above the $11 base: KSA −23.0% to −1.3%, UAE −34.2% to
  −4.0%. Capex, specific yield, the debt rate and the DC/AC ratio follow. In
  KSA, only capex at $450/kW (1.8%) and the high specific yield (0.1%) lift
  equity IRR above zero; in the UAE, nothing does. No single input reaches the
  8% target.

## Limitations
v1 simplifications:
- Flat tariff and O&M.
- All capacity reaches COD together (no phased COD).
- Pro-rata debt/equity funding during construction.
- Interest during construction capitalised into debt.
- No DSRA.
- No tax-loss carry-forward.
- Zakat approximated as 2.5% of profit.
- Construction period fixed at 2 years.

## Sources
- Hatton, L., Staffell, I., Jansen, M., Oluleye, G., & Hawkes, A. (2026).
  *Historical and future projected costs of capital for ten energy
  technologies across 176 countries* [Dataset]. Zenodo.
  https://doi.org/10.5281/zenodo.18662192 — licensed CC BY 4.0.
  Used for: discount-rate defaults (`data/wacc/WACC_ESTIMATES_WIDE.csv`).

- The five `data/wacc/yearly-costsofcapital-national-solar-*.csv` files:
  Exported from the WACC Forecaster (https://wacc-forecaster.streamlit.app),
  built by Hatton et al. on the CC BY 4.0 dataset above. Used for: cost of
  capital component breakdown.

- IRENA (2026), *Renewable power generation costs in 2025*, International
  Renewable Energy Agency, Abu Dhabi. ISBN 978-92-9260-749-4.
  https://www.irena.org/-/media/Files/IRENA/Agency/Publication/2026/Jul/IRENA_TEC_RPGC_in_2025_2026.pdf
  © IRENA 2026; used with acknowledgement per IRENA's terms.
  Used for: O&M default (Table A4), capex upper bound (Fig 3.2),
  real WACC cross-check (Table A2), LCOE comparison (Fig 3.7).

## Disclaimer and feedback
Personal learning project, not investment advice. I built this model myself from public sources to learn project finance modelling and Python. It has not been reviewed or validated by industry experts, developers, lenders or other market participants, and its results may be wrong. Please don't use it for investment, lending or policy decisions. If you have better data or spot an error, I'd be glad to hear from you: [open an issue on GitHub](https://github.com/sarah-adam29/solar-project-finance/issues) or [message me on LinkedIn](https://www.linkedin.com/in/sarah-adam-a24949b1/).

## Licence
MIT. See [LICENSE](LICENSE).
