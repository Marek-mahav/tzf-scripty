import pandas as pd
from modules.config_manager import load_config
from modules.universe_manager import get_universe
from modules.metadata_manager import enrich_and_purge
from modules.data_manager import get_historical_prices
from modules.analysis_manager import analyze_universe

def main():
    cfg = load_config()
    print("Loaded API key:", cfg["universe"]["api_key"])

    universe_df = get_universe(cfg)
    print(f"Before purge: {len(universe_df)} ETFs")

    filtered_df = enrich_and_purge(universe_df, cfg)
    print(f"After metadata purge: {len(filtered_df)} ETFs")

    cols = ["symbol", "name", "price"]
    print(filtered_df[cols].head(10))

    symbols = filtered_df["symbol"].head(10).tolist()
    price_df = get_historical_prices(symbols, cfg)
    print("Historical prices shape:", price_df.shape)

    metrics = analyze_universe(price_df, cfg)
    print("Sample metrics for first 5 ETFs:")
    for m, series in metrics.items():
        print(f"{m}:", series.head(5).to_dict())

    # vytvorenie reportov
    from modules.report_manager import write_reports
    metrics_df = pd.DataFrame(metrics).T
    metrics_df.index.name = "symbol"
    write_reports(metrics_df, price_df, cfg)

if __name__ == "__main__":
    main()
