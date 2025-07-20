import pandas as pd
import pytest
from script_a.dashboard import heal_metrics_df, safe_filter

@pytest.fixture
def sample_df():
    # DataFrame s chýbajúcimi stĺpcami `var` a `sharpe`
    return pd.DataFrame({
        "symbol": ["A", "B", "C"],
        "volatility": [0.1, 0.2, 0.3]
    }).set_index("symbol")

def test_heal_metrics_df_adds_missing_cols(sample_df):
    df = heal_metrics_df(sample_df.copy())
    # Po oprave musí mať všetky tri stĺpce
    assert set(df.columns) >= {"volatility", "sharpe", "var"}
    # Originálne volatility hodnoty ostali
    assert df.loc["A", "volatility"] == pytest.approx(0.1)
    # Novovytvorené stĺpce sú 0.0
    assert all(df["sharpe"] == 0.0)
    assert all(df["var"]    == 0.0)

@pytest.mark.parametrize("col,sel,expected", [
    ("volatility", (0.05, 0.15), ["A"]),
    ("volatility", (0.0, 1.0),    ["A","B","C"]),
    ("volatility", (0.25, 0.5),   ["C"]),
])
def test_safe_filter_ranges(sample_df, col, sel, expected):
    df_healed = heal_metrics_df(sample_df.copy())
    filtered = safe_filter(df_healed, col, sel)
    assert sorted(filtered.index.tolist()) == sorted(expected)

def test_safe_filter_adds_missing_col(sample_df):
    df_healed = heal_metrics_df(sample_df.copy())
    # `sharpe` missing, ale safe_filter ho doplní a potom použije
    out = safe_filter(df_healed, "sharpe", (0.0, 1.0))
    # všetky riadky, pretože default je 0.0 v každom
    assert sorted(out.index.tolist()) == ["A","B","C"]
