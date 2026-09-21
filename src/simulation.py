"""Wire atmosphere, fuel tank, inerting system and controller together."""
import pandas as pd

from .atmosphere import FlightProfile, isa_temperature, isa_pressure
from .fuel_tank import FuelTank
from .inerting import InertingSystem
from .controller import PIController


def run_simulation(dt=1.0, flight=None, tank=None, inerting=None, controller=None):
    flight = flight or FlightProfile()
    tank = tank or FuelTank()
    inerting = inerting or InertingSystem()
    controller = controller or PIController()

    inerting.initialize(isa_pressure(0.0), tank.ullage_volume(), tank.T_ullage)

    n_steps = int(flight.t_total // dt) + 1
    records = []

    for i in range(n_steps):
        t = i * dt
        h = flight.altitude(t)
        phase = flight.phase(t)
        T_amb = isa_temperature(h)
        P_amb = isa_pressure(h)

        x_o2 = inerting.o2_fraction()
        u_cmd = controller.compute_flow(x_o2, dt, u_max_now=inerting.max_flow(P_amb))

        burn = tank.step(dt, phase, T_amb)
        V_ullage = tank.ullage_volume()
        inert_flow = inerting.step(dt, u_cmd, P_amb, V_ullage, tank.T_ullage, P_amb)

        records.append({
            "t_s": t, "t_min": t / 60.0, "phase": phase, "altitude_m": h,
            "fuel_mass_kg": tank.fuel_mass, "ullage_volume_m3": V_ullage,
            "tank_pressure_Pa": P_amb, "tank_temperature_K": tank.T_ullage,
            "o2_fraction": inerting.o2_fraction(), "inert_flow_mol_s": inert_flow,
            "fuel_burn_kg_s": burn,
        })

    return pd.DataFrame.from_records(records)


if __name__ == "__main__":
    df = run_simulation()
    print(df.tail())
    print(f"Final O2 fraction: {df['o2_fraction'].iloc[-1]:.3f}")