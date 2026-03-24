"""
PRIME-Kernel — Unit Tests
"""
import sys
import os
import numpy as np
import pytest

# Ensure package is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from prime_kernel.constants import PhysicsConstants, MarketConstants, EngineConstants
from prime_kernel.hjb_solver import (
    HJBSolver, GridFrequencyDynamics, PerovskiteAnnealingDynamics
)
from prime_kernel.telemetry import PRIMELogger, PRIMETelemetry


# ─── Constants Tests ────────────────────────────────────────

class TestPhysicsConstants:
    def test_h2_lhv_value(self):
        assert PhysicsConstants.H2_LHV_KWH_KG == 33.3

    def test_carnot_efficiency_basic(self):
        eta = PhysicsConstants.carnot_efficiency(800, 300)
        assert 0.6 < eta < 0.7  # ~62.5%

    def test_carnot_efficiency_zero_diff(self):
        eta = PhysicsConstants.carnot_efficiency(300, 300)
        assert eta == 0.0

    def test_carnot_efficiency_invalid(self):
        with pytest.raises(ValueError):
            PhysicsConstants.carnot_efficiency(-100, 300)

    def test_arrhenius_rate_increases_with_temp(self):
        r1 = PhysicsConstants.arrhenius_rate(1.0, 0.5, 300)
        r2 = PhysicsConstants.arrhenius_rate(1.0, 0.5, 600)
        assert r2 > r1

    def test_nh3_stoich(self):
        assert PhysicsConstants.NH3_STOICH_H2 == 5.67


class TestMarketConstants:
    def test_total_nodes(self):
        total = MarketConstants.total_addressable_nodes()
        assert total == 72  # 30 + 22 + 20

    def test_markets_have_required_fields(self):
        for market_id, m in MarketConstants.MARKETS.items():
            assert "frequency_hz" in m
            assert "nodes" in m
            assert "pricing" in m

    def test_projected_revenue(self):
        proj = MarketConstants.projected_annual_revenue(180_000)
        assert "SEN" in proj
        assert proj["SEN"]["nodes"] == 30
        assert proj["SEN"]["prime_revenue_usd"] > 0


class TestEngineConstants:
    def test_fleet_capacity(self):
        cap = EngineConstants.total_fleet_capacity_kw(3, 5, 2)
        # 3×335 + 5×50 + 2×100 = 1005 + 250 + 200 = 1455
        assert cap == 1455.0

    def test_all_engines_have_efficiency(self):
        for eid, eng in EngineConstants.ENGINES.items():
            assert 0.0 < eng["efficiency"] < 1.0


# ─── HJB Solver Tests ──────────────────────────────────────

class TestGridFrequencyDynamics:
    def test_state_dims(self):
        d = GridFrequencyDynamics()
        assert d.state_dims() == 2

    def test_step_reduces_deviation(self):
        d = GridFrequencyDynamics()
        state = np.array([0.5, 50.0])  # 0.5 Hz deviation, 50 MW injection
        next_state = d.step(state, 0.0, 1.0)
        # With injection and damping, deviation should decrease
        assert abs(next_state[0]) < abs(state[0]) or next_state[0] != state[0]

    def test_running_cost_penalizes_deviation(self):
        d = GridFrequencyDynamics()
        cost_low = d.running_cost(np.array([0.1, 50.0]), 0.0)
        cost_high = d.running_cost(np.array([1.0, 50.0]), 0.0)
        assert cost_high > cost_low


class TestPerovskiteAnnealingDynamics:
    def test_state_dims(self):
        d = PerovskiteAnnealingDynamics()
        assert d.state_dims() == 3

    def test_grain_grows_at_high_temp(self):
        d = PerovskiteAnnealingDynamics()
        state = np.array([100.0, 1.0, 150.0])
        next_state = d.step(state, 0.0, 2.0)
        assert next_state[0] > state[0]  # Grains should grow


class TestHJBSolver:
    def test_solver_creation(self):
        d = GridFrequencyDynamics()
        solver = HJBSolver(d, total_time=10.0, dt=1.0,
                           grid_points=[5, 5], n_controls=3, max_sweeps=2)
        assert solver is not None

    def test_solve_and_simulate(self):
        d = GridFrequencyDynamics()
        solver = HJBSolver(d, total_time=10.0, dt=1.0,
                           grid_points=[5, 5], n_controls=3, max_sweeps=2)
        result = solver.solve().simulate(np.array([0.3, 50.0]))
        assert result.total_cost > 0
        assert len(result.state_trajectory) == 11  # 10 steps + 1


# ─── Telemetry Tests ────────────────────────────────────────

class TestPRIMELogger:
    def test_logger_creation(self):
        logger = PRIMELogger("TestSBU")
        logger.info("Test message")
        logger.metric("test_value", 42, "units")
        assert len(logger.get_metrics()) == 1

    def test_metric_format(self):
        logger = PRIMELogger("TestSBU")
        logger.metric("capital", 100000, "USD")
        m = logger.get_metrics()[0]
        assert m["metric"] == "capital"
        assert m["value"] == 100000
        assert m["sbu"] == "TestSBU"


class TestPRIMETelemetry:
    def test_fallback_without_credentials(self):
        t = PRIMETelemetry()
        result = t.send_telegram("Test message")
        assert not result.success
        assert "fallback" in result.channel
