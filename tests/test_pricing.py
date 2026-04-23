"""tests/test_pricing.py — Unit tests for options pricing."""
import sys, math
import numpy as np
import pytest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from pricing.black_scholes import BlackScholes, OptionParams, implied_volatility
from pricing.monte_carlo   import price_european, price_asian, price_barrier
from pricing.risk_metrics  import historical_var, parametric_var, conditional_var

ATM = OptionParams(100,100,1.0,0.05,0.20,"call")
PUT = OptionParams(100,100,1.0,0.05,0.20,"put")
ITM = OptionParams(110,100,1.0,0.05,0.20,"call")
OTM = OptionParams(90, 100,1.0,0.05,0.20,"call")


class TestBlackScholes:
    def test_call_positive(self):
        assert BlackScholes(ATM).price() > 0

    def test_put_call_parity(self):
        call = BlackScholes(ATM).price()
        put  = BlackScholes(PUT).price()
        assert abs(call - put - 100 + 100*math.exp(-0.05)) < 0.001

    def test_itm_greater_otm(self):
        assert BlackScholes(ITM).price() > BlackScholes(OTM).price()

    def test_delta_call_range(self):
        assert 0 < BlackScholes(ATM).delta() < 1

    def test_delta_put_negative(self):
        assert -1 < BlackScholes(PUT).delta() < 0

    def test_gamma_positive(self):
        assert BlackScholes(ATM).gamma() > 0

    def test_vega_positive(self):
        assert BlackScholes(ATM).vega() > 0

    def test_theta_negative(self):
        assert BlackScholes(ATM).theta() < 0

    def test_higher_vol_higher_price(self):
        lo = BlackScholes(OptionParams(100,100,1,0.05,0.10)).price()
        hi = BlackScholes(OptionParams(100,100,1,0.05,0.40)).price()
        assert hi > lo

    def test_expired_intrinsic(self):
        p = BlackScholes(OptionParams(110,100,0,0.05,0.20,"call")).price()
        assert abs(p - 10.0) < 0.01


class TestImpliedVol:
    def test_iv_recovers_sigma(self):
        price = BlackScholes(ATM).price()
        iv    = implied_volatility(price, ATM)
        assert abs(iv - ATM.sigma) < 0.001

    def test_iv_positive(self):
        price = BlackScholes(ATM).price()
        assert implied_volatility(price, ATM) > 0


class TestMonteCarlo:
    def test_european_close_to_bs(self):
        bs_p = BlackScholes(ATM).price()
        mc   = price_european(100,100,1,0.05,0.20,"call",n_paths=20000)
        assert abs(mc.price - bs_p) < 0.5

    def test_asian_leq_european(self):
        eu = price_european(100,100,1,0.05,0.20,"call",n_paths=5000)
        as_ = price_asian(100,100,1,0.05,0.20,"call",n_paths=5000)
        assert as_.price <= eu.price + 0.5

    def test_paths_shape(self):
        r = price_european(100,100,1,0.05,0.20,n_paths=1000)
        assert r.paths.shape[0] <= 200 and r.paths.shape[1] > 1

    def test_ci_contains_price(self):
        r = price_european(100,100,1,0.05,0.20,n_paths=5000)
        assert r.confidence_low <= r.price <= r.confidence_high


class TestRiskMetrics:
    def setup_method(self):
        np.random.seed(42)
        self.returns = np.random.normal(0,1,1000)

    def test_hvar_positive(self):
        assert historical_var(self.returns,0.95) > 0

    def test_cvar_geq_var(self):
        hv = historical_var(self.returns,0.95)
        cv = conditional_var(self.returns,0.95)
        assert cv >= hv - 0.01

    def test_higher_confidence_higher_var(self):
        assert historical_var(self.returns,0.99) >= historical_var(self.returns,0.90)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
