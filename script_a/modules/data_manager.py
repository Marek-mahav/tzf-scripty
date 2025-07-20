import os
import json
import requests
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed

def get_historical_prices(symbols, cfg):
    api_key = cfg["universe"]["api_key"]
    days = cfg["data"]["history_days"]
    cache_dir = os.path.join("cache", "historical")
    os.makedirs(cache_dir, exist_ok=True)

    def fetch(sym):
        cache_file = os.path.join(cache_dir, f"{sym}.json")
        if os.path.exists(cache_file):
            with open(cache_file, "r") as f:
                data = json.load(f)
        else:
            url = (
                f"https://financialmodelingprep.com/"
                f"api/v3/historical-price-full/{sym}"
                f"?timeseries={days}&apikey={api_key}"
            )
            resp = requests.get(url)
            data = resp.json()
            with open(cache_file, "w") as f:
                json.dump(data, f)
        hist = data.get("historical", [])
        if hist:
            return sym, pd.Series({d["date"]: d["close"] for d in hist})
        else:
            return sym, pd.Series(dtype=float)

    results = {}
    batch_size = 50
    for i in range(0, len(symbols), batch_size):
        batch = symbols[i:i+batch_size]
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = executor.map(fetch, batch)
            for sym, series in futures:
                results[sym] = series

    return pd.DataFrame(results)
