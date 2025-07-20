import numpy as np

def analyze_universe(price_df, cfg):
    # výpočet denného výnosu
    # explicitne bez fill_method, aby sme sa zbavili varovania
    returns = price_df.pct_change(fill_method=None).dropna(how='all')
    metrics = {}
    
    # volatility: std dev of returns
    metrics['volatility'] = returns.std() * np.sqrt(252)
    
    # VaR 95%: 5th percentile of returns
    metrics['var'] = returns.quantile(0.05)
    
    # Sharpe ratio
    rf = cfg['analysis']['sharpe_risk_free_rate'] / 252
    metrics['sharpe'] = (returns.mean() - rf) / returns.std()
    
    return metrics
