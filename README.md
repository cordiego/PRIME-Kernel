# PRIME-Kernel

**Shared Core Library — PRIMEnergeia S.A.S.**

Common physics, control, telemetry, and business logic shared across all PRIMEnergeia Strategic Business Units.

## SBU Coverage

| SBU | Module Used | Purpose |
|-----|------------|---------|
| 🔌 PRIME Grid | `hjb_solver.GridFrequencyDynamics` | HJB frequency control |
| ⚡ PRIME Power | `constants.EngineConstants` | Engine fleet specs |
| ♻️ PRIME Circular | `constants.PhysicsConstants` | Material recovery calcs |
| 📈 PRIME Quant | `telemetry.PRIMETelemetry` | Trade notifications |
| 🧪 PRIME Materials | `hjb_solver.PerovskiteAnnealingDynamics` | Annealing optimization |

## Installation

```bash
pip install -e .
```

## Usage

```python
from prime_kernel.constants import PhysicsConstants, MarketConstants
from prime_kernel.hjb_solver import HJBSolver, GridFrequencyDynamics
from prime_kernel.telemetry import PRIMELogger, PRIMETelemetry

# Physics
eta = PhysicsConstants.carnot_efficiency(800, 300)

# HJB Control
dynamics = GridFrequencyDynamics(nominal_freq=60.0)
solver = HJBSolver(dynamics, total_time=60.0, dt=0.5)
result = solver.solve().simulate(initial_state=np.array([0.3, 50.0]))

# Notifications
telemetry = PRIMETelemetry()
telemetry.notify_grid_rescue("VZA-400", 57811, 0.9996)
```

## License

Proprietary — PRIMEnergeia S.A.S. All rights reserved.
