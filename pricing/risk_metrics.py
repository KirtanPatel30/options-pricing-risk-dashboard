"""pricing/risk_metrics.py — VaR, CVaR, scenario P&L."""

import numpy as np
from scipy.stats import norm


def historical_var(returns, confidence=0.95):
    return float(-np.percentile(returns, (1-confidence)*100))

def parametric_var(returns, confidence=0.95):
    return float(-(returns.mean() + norm.ppf(1-confidence)*returns.std()))

def conditional_var(returns, confidence=0.95):
    var = historical_var(returns, confidence)
    losses = -returns
    return float(losses[losses > var].mean())

def generate_portfolio_returns(positions, n_days=252, seed=42):
    from pricing.black_scholes import BlackScholes, OptionParams
    np.random.seed(seed)
    total = np.zeros(n_days)
    for pos in positions:
        qty   = pos.get("quantity", 1)
        sigma = pos.get("sigma", 0.20)
        shocks= np.random.normal(0, sigma/np.sqrt(252), n_days)
        p0    = BlackScholes(OptionParams(**{k:v for k,v in pos.items() if k!="quantity"})).price()
        S0    = pos["S"]
        pnl   = []
        for shock in shocks:
            p_new = BlackScholes(OptionParams(
                S=S0*(1+shock), K=pos["K"],
                T=max(pos["T"]-1/252, 1e-6),
                r=pos["r"], sigma=pos["sigma"],
                option_type=pos.get("option_type","call"),
                q=pos.get("q",0.0)
            )).price()
            pnl.append((p_new - p0) * qty)
            p0 = p_new
        total += np.array(pnl)
    return total

def scenario_pnl(S, K, T, r, sigma, option_type, quantity,
                 n_spot=20, n_vol=20):
    from pricing.black_scholes import BlackScholes, OptionParams
    p0     = BlackScholes(OptionParams(S,K,T,r,sigma,option_type)).price()
    spots  = np.linspace(S*0.70, S*1.30, n_spot)
    vols   = np.linspace(max(0.01, sigma-0.15), sigma+0.25, n_vol)
    grid   = np.zeros((n_vol, n_spot))
    for i,v in enumerate(vols):
        for j,s in enumerate(spots):
            p = BlackScholes(OptionParams(s,K,T,r,v,option_type)).price()
            grid[i,j] = (p-p0)*quantity
    return spots, vols, grid
