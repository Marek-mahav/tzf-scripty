import streamlit as st
import pandas as pd

from modules.config_manager import load_config
from modules.universe_manager import get_universe
from modules.metadata_manager import enrich_and_purge
from modules.data_manager import get_historical_prices
from modules.analysis_manager import analyze_universe

@st.cache_data
def load_data(cfg):
    """
    Načíta univerzum, vyčistí ho, stiahne historické ceny
    a vypočíta metriky pre každý symbol.
    """
    uni = get_universe(cfg)
    filtered = enrich_and_purge(uni, cfg)
    symbols = filtered["symbol"].tolist()

    demo_n = cfg.get("data", {}).get("demo_n")
    if demo_n:
        symbols = symbols[:demo_n]

    prices = get_historical_prices(symbols, cfg)
    metrics = analyze_universe(prices, cfg)

    # Bez .T – index zostanú tickery
    metrics_df = pd.DataFrame(metrics)
    metrics_df.index.name = "symbol"
    return filtered, prices, metrics_df

def heal_metrics_df(df: pd.DataFrame) -> pd.DataFrame:
    """
    Pretransformuje názvy stĺpcov na lowercase a doplní
    chýbajúce metriky volatility, sharpe, var nulovými hodnotami.
    """
    df.columns = df.columns.str.lower()
    for col in ["volatility", "sharpe", "var"]:
        if col not in df.columns:
            df[col] = 0.0
    return df

def safe_slider(label: str, lo: float, hi: float, help_text: str = "") -> tuple[float, float]:
    """
    Bezpečný sidebar slider s tooltipom.
    Keď lo >= hi, vráti (lo, hi) bez vykreslenia slideru.
    """
    if lo >= hi:
        return lo, hi
    return st.sidebar.slider(
        label,
        lo,
        hi,
        (lo, hi),
        help=help_text
    )

def safe_filter(df: pd.DataFrame, col: str, sel: tuple[float, float]) -> pd.DataFrame:
    """
    Zabezpečí, že DataFrame má stĺpec col (inak ho doplní nulami),
    a potom aplikuje intervalový filter podľa sel.
    """
    if col not in df.columns:
        df[col] = 0.0
    return df[(df[col] >= sel[0]) & (df[col] <= sel[1])]

def main():
    st.title("ETF Analytics Dashboard")
    cfg = load_config()

    # 1) Načíta dáta a metriky
    filtered_df, price_df, metrics_df = load_data(cfg)

    # 2) Self-healing transformácia
    metrics_df = heal_metrics_df(metrics_df)

    # 3) Rozsahy pre slidery
    vol_min, vol_max       = float(metrics_df["volatility"].min()), float(metrics_df["volatility"].max())
    sharpe_min, sharpe_max = float(metrics_df["sharpe"].min()),     float(metrics_df["sharpe"].max())
    var_min, var_max       = float(metrics_df["var"].min()),        float(metrics_df["var"].max())

    # 4) Sidebar: slidery + výber symbolov
    st.sidebar.header("Filter ETF")
    vol_sel = safe_slider(
        "Volatility", vol_min, vol_max,
        help_text="Ročná volatilita ETF (štandardná odchýlka × √252)"
    )
    sharpe_sel = safe_slider(
        "Sharpe", sharpe_min, sharpe_max,
        help_text="Sharpe ratio: (mean return − risk-free) / štandardná odchýlka"
    )
    var_sel = safe_slider(
        "VAR", var_min, var_max,
        help_text="Value at Risk (95%): 5. percentil denného výnosu"
    )

    symbols_sel = st.sidebar.multiselect(
        "Select symbols",
        options=metrics_df.index.tolist(),
        default=metrics_df.index[:5]
    )

    # 5) Aplikuj filter na metriky
    df = metrics_df.copy()
    df = safe_filter(df, "volatility", vol_sel)
    df = safe_filter(df, "sharpe",    sharpe_sel)
    df = safe_filter(df, "var",       var_sel)
    df = df[df.index.isin(symbols_sel)]

    # 6) Download tlačidlo pre CSV
    csv = df.to_csv(index=True).encode("utf-8")
    st.download_button(
        label="⬇️ Stiahnuť filtrované dáta (CSV)",
        data=csv,
        file_name="filtered_etf_metrics.csv",
        mime="text/csv",
        help="Export aktuálne filtrovaných metrík do CSV"
    )

    # 7) Zobraz tabuľku
    st.subheader("Filtered ETF Metrics")
    st.dataframe(
        df.style.format({
            "volatility": "{:.2%}",
            "sharpe":     "{:.2f}",
            "var":        "{:.2%}"
        })
    )

    # 8) Price Time Series chart
    st.subheader("Price Time Series")
    if symbols_sel:
        chart_data = price_df[symbols_sel]
        st.line_chart(chart_data)

if __name__ == "__main__":
    main()
