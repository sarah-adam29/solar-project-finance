"""Print a short KSA and UAE summary: uv run python -m model"""

from model.engine import run_model
from model.inputs import COUNTRIES, load_inputs
from model.solve import implied_discount_rate


def _percent(value: float | None) -> str:
    return "n/a" if value is None else f"{value:.2%}"


def main() -> None:
    rows = {
        "LCOE (US cents/kWh)": [],
        "PPA tariff (US cents/kWh)": [],
        "Project IRR": [],
        "Equity IRR": [],
        "Minimum DSCR": [],
        "Project NPV (USD m)": [],
        "Discount rate": [],
        "Implied discount rate": [],
    }
    for country in COUNTRIES:
        inputs = load_inputs(country)
        results = run_model(inputs)
        rows["LCOE (US cents/kWh)"].append(f"{results.lcoe_cents_per_kwh:.2f}")
        rows["PPA tariff (US cents/kWh)"].append(f"{inputs.ppa_tariff * 100:.2f}")
        rows["Project IRR"].append(_percent(results.project_irr))
        rows["Equity IRR"].append(_percent(results.equity_irr))
        rows["Minimum DSCR"].append(f"{results.min_dscr:.2f}x")
        rows["Project NPV (USD m)"].append(f"{results.project_npv / 1e6:,.1f}")
        rows["Discount rate"].append(_percent(inputs.discount_rate))
        rows["Implied discount rate"].append(_percent(implied_discount_rate(country)))

    print(f"{'':<28}" + "".join(f"{country:>10}" for country in COUNTRIES))
    for label, values in rows.items():
        print(f"{label:<28}" + "".join(f"{value:>10}" for value in values))


if __name__ == "__main__":
    main()
