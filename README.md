# Aircraft Fuel Tank & Inerting System Simulation

A physics-based Python simulation of an aircraft wing fuel tank coupled to an OBIGGS-style (On-Board Inert Gas Generation System) flammability-reduction system, closed with a PI controller regulating ullage oxygen concentration.

Models the full chain: **atmosphere → flight profile → fuel consumption → ullage thermodynamics → inert-gas dilution → closed-loop O₂ control.**

---

## Why this project

Modern transport aircraft (A320, A350, 787, etc.) are required to reduce ullage flammability in the center wing tank per FAA/EASA rules (14 CFR 25.981) by injecting nitrogen-enriched air (NEA) to dilute oxygen concentration below a target threshold, typically ~12%. This project builds a reduced-order model of that system end-to-end — from atmosphere and flight profile through to a closed-loop controller — connecting control systems, thermodynamics, and aerospace systems engineering.

```
physics → mathematical model → Python simulation → system behaviour → control decision
```

---

## System overview

```
Fuel Tank
   │
   ├── Fuel consumption (phase-dependent burn rate)
   ├── Ullage volume (grows as fuel burns)
   ├── Tank pressure (vented → tracks ambient/ISA)
   ├── Temperature (first-order lag toward ambient)
   └── Ullage O₂ concentration
             │
             ▼
      Inerting system (OBIGGS)
             │
             ▼
      Nitrogen-enriched air (NEA) injection
```

Closed-loop control:

```
O₂ concentration
       ↓
  PI Controller
       ↓
Inert-gas flow rate
       ↓
   Fuel Tank / Ullage
       ↓
O₂ concentration  ↺ (fed back)
```

---

## Physics modeled

- **Atmosphere** — International Standard Atmosphere (ISA), troposphere (≤11,000 m): temperature lapse and barometric pressure formula.
- **Flight profile** — three-phase climb / cruise / descent altitude ramp.
- **Fuel consumption** — phase-dependent burn rate (climb > cruise > descent), integrated over time.
- **Ullage volume** — tank volume minus liquid fuel volume; grows as fuel burns.
- **Tank pressure** — tank is vented, so ullage pressure tracks ambient pressure at all times (standard for unpressurized wing tanks).
- **Ullage temperature** — first-order thermal lag toward ambient temperature (models tank structure thermal inertia).
- **Inerting (OBIGGS)** — NEA (5% O₂ by default) injected into the ullage; an ideal-gas-law mole balance determines how many additional moles enter as ambient air or vent overboard each timestep, so the ullage always satisfies `PV = nRT` exactly.
- **NEA supply derating** — inert-gas flow capacity decreases with altitude (bleed-air-limited), floored at 20% of sea-level capacity.
- **Control** — PI controller commands inert-gas flow rate to drive ullage O₂ toward a 12% target, with output saturation and anti-windup.

---

## Why PI, not PID

- **Integral action** drives **steady-state error to zero** — the actual requirement here is holding ullage O₂ at the 12% target indefinitely, not just getting close to it.
- **No derivative term** because:
  - The plant is slow — ullage volume changes over minutes (fuel burn timescale), not seconds; there's no fast transient to damp.
  - Real O₂ sensors are noisy; differentiating a noisy error signal mostly amplifies noise rather than improving tracking.
  - The system is already flow-rate-limited (`u_max`), so P+I saturates gracefully without needing derivative damping.
  - Real aircraft OBIGGS controllers are typically simple PI or schedule-based, so this is representative of actual industry practice.
- **Anti-windup** is implemented explicitly: the integral term only accumulates while the controller output is *not* saturated, preventing overshoot once the inert-flow limit is no longer binding.

---

## Repository structure

```
fuel-inerting-system-simulation/
│
├── src/
│   ├── __init__.py
│   ├── atmosphere.py       ISA model + flight altitude profile
│   ├── fuel_tank.py        fuel mass / ullage volume / temperature
│   ├── inerting.py         OBIGGS mole-balance O2 dilution model
│   ├── controller.py       PI controller with anti-windup
│   ├── simulation.py       time-stepped integration loop
│   └── plotting.py         result plots
│
├── data/
│   └── simulation_output.csv   (generated)
│
├── tests/
│   └── test_simulation.py
│
├── main.py
├── simulation_analysis.png     (generated)
├── requirements.txt
└── README.md
```

---

## Key formulas

| Quantity | Formula |
|---|---|
| ISA temperature | `T(h) = T0 − L·h` |
| ISA pressure | `P(h) = P0·(T(h)/T0)^(g0·M/(R·L))` |
| Fuel mass update | `m(t+dt) = m(t) − burn_rate(phase)·dt` |
| Ullage volume | `V_ullage = V_tank − m_fuel/ρ_fuel` |
| Ullage temperature | `T += (T_ambient − T)/τ · dt` |
| Total ullage moles (ideal gas law) | `n_total = P·V / (R·T)` |
| O₂ fraction | `x_O2 = n_O2 / (n_O2 + n_N2)` |
| NEA supply derating | `flow_max = flow_max,SL · max(P/P0, f_min)` |
| PI control law | `u = Kp·error + Ki·∫error dt`, saturated to `[u_min, u_max]` |

Full derivations and explanations are in the code comments in each module.

---

## Setup

```bash
git clone https://github.com/RyanKhurana9/fuel-inerting-system-simulation.git
cd fuel-inerting-system-simulation

python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install -r requirements.txt
```

## Run

```bash
python main.py
```

This generates:
- `data/simulation_output.csv` — full second-by-second time history
- `simulation_analysis.png` — 6-panel plot (fuel mass, ullage volume, tank pressure, temperature, O₂ concentration, inert-gas flow)
- Console output: summary statistics via `df.describe()`

## Test

```bash
pytest tests/ -v
```

Covers: ISA correctness at sea level, monotonic fuel depletion, O₂ fraction bounds, convergence toward the O₂ target, ullage volume growth, controller saturation, anti-windup behavior, and exact ideal-gas-law conservation in the mole balance.

---

## Data

No external dataset is used or required — all data is **generated by the simulation itself** via physics-based numerical integration (ISA equations, fuel burn, and the mole balance), not loaded from a real-world source. Constants (tank volume, burn rates, NEA purity, target O₂%) can optionally be replaced with public aircraft type-certificate figures for added realism.

---

## Limitations / simplifying assumptions

- Troposphere-only ISA (valid to 11,000 m).
- No fuel vapor pressure / Reid vapor pressure modeling.
- Vented-tank pressure assumption ignores transient pressure relief valve dynamics.
- Constant burn rate per flight phase rather than a full thrust/fuel-flow model.
- NEA purity and flow-capacity numbers are illustrative, not certified type-design data.

---

## Possible extensions

- Replace constant burn rates with a thrust/fuel-flow model driven by an aircraft performance model.
- Add a non-linear ullage thermodynamics model (heat transfer through tank walls, fuel-vapor equilibrium).
- Model transient pressure-relief-valve dynamics instead of assuming instantaneous venting.
- Swap the PI controller for a gain-scheduled or model-predictive controller and compare performance.
- Validate against public OBIGGS performance data or FAA flammability reduction rule test cases.