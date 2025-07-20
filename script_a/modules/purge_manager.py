def purge_universe(universe_df, cfg):
    p = cfg["purge"]
    if not p["enabled"]:
        return universe_df
    df = universe_df.copy()
    if p["blacklist"]:
        df = df[~df["symbol"].isin(p["blacklist"])]
    return df
