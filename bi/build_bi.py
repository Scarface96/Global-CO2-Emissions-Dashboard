"""Export model-ready tables for Power BI (and Tableau).

    python -m bi.build_bi

Writes bi/data/*.csv and bi/kpis.json (the headline numbers your dashboard should show,
so you can check a Power BI build against this repo and the existing Tableau workbook).

Country tables hold real countries only. World totals are kept in their own table because
countries do not add up to the world figure (international shipping and aviation are
counted only at world level), so summing countries would understate global emissions.
"""

import json
from pathlib import Path

import pandas as pd

from analysis import data as d

OUT = Path(__file__).resolve().parent


def tables(df: pd.DataFrame) -> dict:
    c = d.countries(df)
    c = c[c["co2"].notna()]
    fact_country_year = c[[
        "iso_code", "year", "population", "gdp", "co2", "co2_per_capita",
        "cumulative_co2", "share_global_co2", "share_global_cumulative_co2",
    ]].sort_values(["iso_code", "year"]).reset_index(drop=True)

    fact_fuel = (
        c[["iso_code", "year"] + d.FUELS]
        .melt(id_vars=["iso_code", "year"], var_name="fuel_code", value_name="fuel_co2")
        .dropna(subset=["fuel_co2"])
        .rename(columns={"fuel_co2": "co2"})
    )
    fact_fuel["fuel"] = fact_fuel["fuel_code"].map(d.FUEL_LABELS)
    fact_fuel = fact_fuel[["iso_code", "year", "fuel", "co2"]].sort_values(["iso_code", "year", "fuel"]).reset_index(drop=True)

    latest = c.sort_values("year").groupby("iso_code").tail(1)
    dim_country = latest[["iso_code", "country", "population"]].rename(columns={"population": "latest_population"})
    dim_country = dim_country.sort_values("country").reset_index(drop=True)

    w = d.world(df)
    fact_world = w.loc[w["co2"].notna(), ["population", "co2", "co2_per_capita", "cumulative_co2"] + d.FUELS].reset_index()
    return {"dim_country": dim_country, "fact_country_year": fact_country_year, "fact_fuel": fact_fuel, "fact_world": fact_world}


def kpis(df: pd.DataFrame) -> dict:
    year = d.latest_year(df)
    w = d.world(df)
    c = d.countries(df)
    r = d.rankings(c, year)
    top = r["total"].iloc[0]
    top_pc = r["per_capita"].iloc[0]
    top_cum = r["cumulative"].iloc[0]
    return {
        "Latest year": year,
        f"World CO2 in {year} (million tonnes)": round(float(w.loc[year, "co2"]), 1),
        f"World CO2 per person in {year} (tonnes)": round(float(w.loc[year, "co2_per_capita"]), 2),
        f"World cumulative CO2 to {year} (million tonnes)": round(float(w.loc[year, "cumulative_co2"]), 0),
        f"Largest emitter in {year}": f"{top['country']} ({top['co2']:,.1f} Mt)",
        f"Highest per person in {year} (1M+ people)": f"{top_pc['country']} ({top_pc['co2_per_capita']:.1f} t)",
        "Largest cumulative emitter": f"{top_cum['country']} ({top_cum['cumulative_co2']:,.0f} Mt)",
        "Countries in the model": int(c.loc[c["co2"].notna(), "iso_code"].nunique()),
    }


def build(out: Path = OUT) -> dict:
    df = d.load()
    t = tables(df)
    (out / "data").mkdir(parents=True, exist_ok=True)
    for name, frame in t.items():
        frame.to_csv(out / "data" / f"{name}.csv", index=False)
    k = kpis(df)
    (out / "kpis.json").write_text(json.dumps(k, indent=2) + "\n")
    return {"tables": t, "kpis": k}


if __name__ == "__main__":
    res = build()
    for name, frame in res["tables"].items():
        print(f"{name}: {len(frame):,} rows")
    print(json.dumps(res["kpis"], indent=2))
