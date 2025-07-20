import os, time, json
import requests, pandas as pd

CACHE_FILE = "cache/universe.json"
CSV_FALLBACK = "data/universe.csv"

def get_universe(cfg):
    api_key = cfg["universe"]["api_key"]
    source = cfg["universe"].get("source", "").lower()

    # 1) Fallback: cache file
    if os.path.exists(CACHE_FILE):
        data_list = json.load(open(CACHE_FILE))
        print(f"get_universe: loaded {len(data_list)} ETF zo {CACHE_FILE}")
        return pd.DataFrame(data_list)

    # 2) Throttled session s retry
    from urllib3.util import Retry
    from requests.adapters import HTTPAdapter

    endpoints = []
    if source == "fmpcloud":
        endpoints.append(f"https://fmpcloud.io/api/v3/etf/list?apikey={api_key}")
    endpoints.append(f"https://financialmodelingprep.com/api/v3/etf/list?apikey={api_key}")

    session = requests.Session()
    retries = Retry(total=3, backoff_factor=1, status_forcelist=[429])
    session.mount("https://", HTTPAdapter(max_retries=retries))

    data_list = None
    for url in endpoints:
        try:
            resp = session.get(url, timeout=10)
        except Exception as e:
            print(f"get_universe: EXCEPTION {url} → {e}")
            continue

        print(f"get_universe: {url} → {resp.status_code}")
        if resp.status_code != 200:
            continue

        payload = resp.json()
        if isinstance(payload, dict):
            arr = payload.get("etfList") or payload.get("symbolsList") or []
        elif isinstance(payload, list):
            arr = payload
        else:
            arr = []

        if arr:
            data_list = arr
            print(f"get_universe: získaných {len(arr)} ETF zo {url}")
            # uložíme pre ďalšie spustenie
            os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
            json.dump(arr, open(CACHE_FILE, "w"), indent=2)
            break

        time.sleep(1)

    # 3) CSV fallback
    if not data_list and os.path.exists(CSV_FALLBACK):
        df = pd.read_csv(CSV_FALLBACK)
        print(f"get_universe: načítaných {len(df)} ETF z {CSV_FALLBACK}")
        return df

    if not data_list:
        print("Error: get_universe stále prázdny – nemáte cache ani CSV fallback.")
        return pd.DataFrame()

    return pd.DataFrame(data_list)
