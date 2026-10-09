import numpy as np
import pandas as pd
import pytest

from analysis import data


@pytest.fixture(scope="module")
def df():
    return data.load()


def test_countries_exclude_aggregates(df):
    c = data.countries(df)
    names = set(c["country"])
    assert "World" not in names and "Africa" not in names and "High-income countries" not in names
    assert {"China", "South Africa", "United States"} <= names


def test_world_fuels_add_up_to_total(df):
    w = data.world(df).loc[2000:]
    parts = w[data.FUELS].sum(axis=1)
    assert np.allclose(parts, w["co2"], rtol=0.01)


def test_rankings(df):
    r = data.rankings(data.countries(df), 2021)
    assert r["total"].iloc[0]["country"] == "China"
    assert r["cumulative"].iloc[0]["country"] == "United States"


def test_responsibility_shares_are_fractions(df):
    t = data.responsibility(df, 2021, ["United States", "China", "Africa"])
    assert t[["share_cumulative", "share_annual", "share_population"]].stack().between(0, 1).all()


def test_indexed_starts_at_100(df):
    ix = data.indexed(data.countries(df), ["United Kingdom"], 1990, 2018)
    first = ix[ix["year"] == 1990].iloc[0]
    assert first["co2_index"] == pytest.approx(100) and first["gdp_index"] == pytest.approx(100)


def test_recent_trend_recovers_a_known_growth_rate():
    years = np.arange(2011, 2022)
    fake = pd.DataFrame({"country": "X", "year": years, "co2": 100 * 1.05 ** (years - 2011)})
    t = data.recent_trend(fake, 2011, 2021, top=1)
    assert t.iloc[0]["annual_change"] == pytest.approx(0.05, abs=1e-9)
