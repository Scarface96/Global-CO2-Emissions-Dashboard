"""Load the Our World in Data CO2 file and shape it for analysis.

Units: co2 and fuel columns are million tonnes (Mt) per year; per-capita columns are
tonnes per person; cumulative_co2 is million tonnes since 1750; gdp is international $.
"""

from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "visualizing_global_co2_data.csv"
FUELS = ["coal_co2", "oil_co2", "gas_co2", "cement_co2", "flaring_co2", "other_industry_co2"]
FUEL_LABELS = {"coal_co2": "Coal", "oil_co2": "Oil", "gas_co2": "Gas", "cement_co2": "Cement", "flaring_co2": "Flaring", "other_industry_co2": "Other industry"}
KEEP = ["country", "year", "iso_code", "population", "gdp", "co2", "co2_per_capita", "cumulative_co2", "share_global_co2", "share_global_cumulative_co2"] + FUELS


def load(path: Path = DATA) -> pd.DataFrame:
    df = pd.read_csv(path, usecols=KEEP)
    assert not df.duplicated(["country", "year"]).any(), "one row per country-year expected"
    return df


def countries(df: pd.DataFrame) -> pd.DataFrame:
    """Real countries only: drop continents, income groups, 'World' and OWID aggregates."""
    iso = df["iso_code"].fillna("")
    return df[iso.str.fullmatch(r"[A-Z]{3}")].copy()


def world(df: pd.DataFrame) -> pd.DataFrame:
    return df[df["country"] == "World"].set_index("year").sort_index()


def latest_year(df: pd.DataFrame) -> int:
    return int(df.loc[df["co2"].notna(), "year"].max())


def rankings(c: pd.DataFrame, year: int, n: int = 10, min_population: float = 1e6) -> dict[str, pd.DataFrame]:
    """Top countries three ways. Per-capita ranking ignores micro-states under 1M people."""
    y = c[c["year"] == year]
    big = y[y["population"] >= min_population]
    return {
        "total": y.nlargest(n, "co2")[["country", "co2"]],
        "per_capita": big.nlargest(n, "co2_per_capita")[["country", "co2_per_capita"]],
        "cumulative": y.nlargest(n, "cumulative_co2")[["country", "cumulative_co2"]],
    }


def responsibility(df: pd.DataFrame, year: int, regions: list[str]) -> pd.DataFrame:
    """Share of all-time emissions, of this year's emissions, and of world population."""
    y = df[df["year"] == year].set_index("country")
    w = y.loc["World"]
    t = pd.DataFrame({
        "share_cumulative": y.loc[regions, "cumulative_co2"] / w["cumulative_co2"],
        "share_annual": y.loc[regions, "co2"] / w["co2"],
        "share_population": y.loc[regions, "population"] / w["population"],
    })
    return t.reset_index()


def indexed(c: pd.DataFrame, names: list[str], base: int, end: int) -> pd.DataFrame:
    """CO2 and GDP as an index (base year = 100) for chosen countries."""
    rows = []
    for name in names:
        g = c[(c["country"] == name) & c["year"].between(base, end)].set_index("year")
        if base not in g.index:
            continue
        rows.append(pd.DataFrame({
            "country": name,
            "year": g.index,
            "co2_index": g["co2"] / g.loc[base, "co2"] * 100,
            "gdp_index": g["gdp"] / g.loc[base, "gdp"] * 100,
        }))
    return pd.concat(rows, ignore_index=True)


def decoupled(c: pd.DataFrame, base: int, end: int, min_co2: float = 10.0) -> pd.DataFrame:
    """Countries whose GDP grew while CO2 fell between two years (sizeable emitters only)."""
    a = c[c["year"] == base].set_index("country")
    b = c[c["year"] == end].set_index("country")
    both = a.index.intersection(b.index)
    t = pd.DataFrame({
        "co2_change": b.loc[both, "co2"] / a.loc[both, "co2"] - 1,
        "gdp_change": b.loc[both, "gdp"] / a.loc[both, "gdp"] - 1,
        "co2_base": a.loc[both, "co2"],
    }).dropna()
    t = t[t["co2_base"] >= min_co2]
    t["decoupled"] = (t["gdp_change"] > 0) & (t["co2_change"] < 0)
    return t.reset_index().sort_values("co2_change")


def recent_trend(c: pd.DataFrame, start: int, end: int, top: int = 25) -> pd.DataFrame:
    """Average yearly % change in CO2 (log-linear fit) for the largest emitters."""
    biggest = c[c["year"] == end].nlargest(top, "co2")["country"]
    rows = []
    for name in biggest:
        g = c[(c["country"] == name) & c["year"].between(start, end)].dropna(subset=["co2"])
        slope = np.polyfit(g["year"], np.log(g["co2"]), 1)[0]
        rows.append({"country": name, "annual_change": np.expm1(slope), "co2_latest": g["co2"].iloc[-1]})
    return pd.DataFrame(rows).sort_values("annual_change")


def explorer_payload(c: pd.DataFrame, w: pd.DataFrame, since: int = 1950) -> dict:
    """Compact per-country series for the in-page country explorer."""
    cols = ["co2", "co2_per_capita"] + FUELS[:4]
    out = {}
    frames = [c[c["year"] >= since], w.reset_index().assign(country="World")[lambda d: d["year"] >= since]]
    for name, g in pd.concat(frames).groupby("country"):
        g = g.sort_values("year")
        if g["co2"].notna().sum() < 10:
            continue
        out[name] = {"year": g["year"].tolist(), **{k: [None if pd.isna(v) else round(float(v), 3) for v in g[k]] for k in cols}}
    return out
