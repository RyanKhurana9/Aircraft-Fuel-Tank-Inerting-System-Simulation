from src.simulation import run_simulation
from src.atmosphere import isa_pressure, isa_temperature, FlightProfile
from src.controller import PIController
from src.inerting import InertingSystem
from src.atmosphere import R_UNIVERSAL


def test_isa_sea_level():
    assert abs(isa_pressure(0.0) - 101325.0) < 1.0
    assert abs(isa_temperature(0.0) - 288.15) < 1e-6

def test_fuel_mass_decreases_monotonically():
    df = run_simulation()
    assert (df["fuel_mass_kg"].diff().dropna() <= 1e-9).all()

def test_o2_fraction_bounded():
    df = run_simulation()
    assert (df["o2_fraction"] >= 0.0).all() and (df["o2_fraction"] <= 0.21).all()

def test_o2_fraction_decreases_toward_target():
    df = run_simulation()
    assert df["o2_fraction"].iloc[-1] < df["o2_fraction"].iloc[0]

def test_ullage_volume_grows_as_fuel_burns():
    df = run_simulation()
    assert df["ullage_volume_m3"].iloc[-1] > df["ullage_volume_m3"].iloc[0]

def test_controller_saturates_at_max_flow():
    c = PIController(kp=100.0)
    u = c.compute(x_o2_measured=0.21, dt=1.0, u_max_now=0.05)
    assert u == 0.05

def test_controller_anti_windup_freezes_integral_when_saturated():
    c = PIController(kp=100.0, ki=1.0)
    c.compute(0.21, dt=1.0, u_max_now=0.01)
    integral_after_1 = c.integral
    c.compute(0.21, dt=1.0, u_max_now=0.01)
    assert c.integral == integral_after_1

def test_mole_balance_conserves_gas_law_exactly():
    inert = InertingSystem()
    inert.initialize(101325.0, 5.0, 288.15)
    inert.step(dt=1.0, inert_flow_cmd=0.1, P_ullage=101325.0,
               V_ullage=5.5, T_ullage=288.15, P_ambient=101325.0)
    n_total = inert.n_o2 + inert.n_n2
    n_expected = 101325.0 * 5.5 / (R_UNIVERSAL * 288.15)
    assert abs(n_total - n_expected) < 1e-6

def test_zero_flight_duration_edge_case():
    df = run_simulation(flight=FlightProfile(t_climb_s=1, t_cruise_s=1, t_descent_s=1))
    assert len(df) > 0