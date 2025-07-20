import pandas as pd

def enrich_and_purge(universe_df, cfg):
    p = cfg["purge"]
    df = universe_df.copy()

    # 1) Filter podľa priemerného objemu – najskôr overíme, ktorý stĺpec existuje
    vol_col = None
    if "volAvg" in df.columns:
        vol_col = "volAvg"
    elif "avgVolume" in df.columns:
        vol_col = "avgVolume"

    if vol_col and p.get("min_average_volume") is not None:
        # nahradíme NaN nulami a potom filtrujeme
        df = df[df[vol_col].fillna(0) >= p["min_average_volume"]]

    # 2) Blacklist
    if p.get("blacklist"):
        df = df[~df["symbol"].isin(p["blacklist"])]

    return df
