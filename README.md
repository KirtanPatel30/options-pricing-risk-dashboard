# ⚡ Options Pricing & Risk Dashboard

> Black-Scholes + Monte Carlo options pricer — full Greeks, implied volatility
> surface, VaR/CVaR risk metrics, scenario analysis, and interactive dashboard.

## Models
- Black-Scholes analytical pricer (Call + Put)
- Monte Carlo simulation — European, Asian, Barrier options
- Greeks: Delta, Gamma, Theta, Vega, Rho
- Implied Volatility via Newton-Raphson solver
- VaR + CVaR (historical & parametric)

## Quick Start
```bash
pip install -r requirements.txt
python run_all.py
streamlit run dashboard/app.py
```

## Resume Bullets
- Implemented Black-Scholes and Monte Carlo options pricing engine computing
  full Greeks (Delta, Gamma, Theta, Vega, Rho) for European, Asian, and Barrier options
- Built Newton-Raphson implied volatility solver; generated 3D vol surface
  showing smile and term structure across 15 strikes and 7 expiries
- Computed portfolio VaR and CVaR via historical simulation; built P&L scenario
  grid across spot × volatility parameter space
- Deployed 5-tab interactive risk dashboard with no-sidebar top-nav layout,
  Monte Carlo path visualization, and live Greeks heatmap
