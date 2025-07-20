from modules.config_manager import load_config
from modules.universe_manager import get_universe

def main():
    cfg = load_config()
    universe_df = get_universe(cfg)
    print(f"Loaded {len(universe_df)} ETFs from FMP API")
    print(universe_df[["symbol", "name", "expenseRatio"]].head(10))

if __name__ == "__main__":
    main()
