"""pricing/monte_carlo.py — Monte Carlo options pricing."""

import numpy as np
from dataclasses import dataclass


@dataclass
class MCResult:
    price: float
    std_error: float
    confidence_low: float
    confidence_high: float
    n_paths: int
    paths: np.ndarray


def _simulate(S, r, sigma, T, n_paths, n_steps, seed=42):
    np.random.seed(seed)
    dt = T / n_steps
    Z  = np.random.standard_normal((n_paths, n_steps))
    px = S * np.exp(np.cumsum((r - 0.5*sigma**2)*dt + sigma*np.sqrt(dt)*Z, axis=1))
    return np.hstack([np.full((n_paths,1), S), px])


def _result(payoffs, r, T, n_paths, paths):
    disc = np.exp(-r*T) * payoffs
    p    = disc.mean()
    se   = disc.std() / np.sqrt(n_paths)
    return MCResult(round(p,4), round(se,6), round(p-1.96*se,4),
                    round(p+1.96*se,4), n_paths, paths[:200])


def price_european(S, K, T, r, sigma, option_type="call",
                   n_paths=10000, n_steps=252, seed=42) -> MCResult:
    paths = _simulate(S, r, sigma, T, n_paths, n_steps, seed)
    S_T   = paths[:,-1]
    pay   = np.maximum(S_T-K, 0) if option_type=="call" else np.maximum(K-S_T, 0)
    return _result(pay, r, T, n_paths, paths)


def price_asian(S, K, T, r, sigma, option_type="call",
                n_paths=10000, n_steps=252, seed=42) -> MCResult:
    paths = _simulate(S, r, sigma, T, n_paths, n_steps, seed)
    avg   = paths[:,1:].mean(axis=1)
    pay   = np.maximum(avg-K, 0) if option_type=="call" else np.maximum(K-avg, 0)
    return _result(pay, r, T, n_paths, paths)


def price_barrier(S, K, T, r, sigma, barrier, barrier_type="down-and-out",
                  option_type="call", n_paths=10000, n_steps=252, seed=42) -> MCResult:
    paths = _simulate(S, r, sigma, T, n_paths, n_steps, seed)
    S_T   = paths[:,-1]
    if   barrier_type == "down-and-out": alive = paths.min(axis=1) > barrier
    elif barrier_type == "up-and-out":   alive = paths.max(axis=1) < barrier
    elif barrier_type == "down-and-in":  alive = paths.min(axis=1) <= barrier
    else:                                alive = paths.max(axis=1) >= barrier
    base  = np.maximum(S_T-K, 0) if option_type=="call" else np.maximum(K-S_T, 0)
    pay   = np.where(alive, base, 0)
    return _result(pay, r, T, n_paths, paths)
