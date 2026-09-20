"""Six standard time-history plots for the simulation."""
import matplotlib.pyplot as plt


def plot_results(df, save_path=None):
    fig, axes = plt.subplots(3, 2, figsize=(12, 10), sharex=True)

    axes[0, 0].plot(df["t_min"], df["fuel_mass_kg"])
    axes[0, 0].set_ylabel("Fuel mass (kg)"); axes[0, 0].set_title("Fuel mass vs time")

    axes[0, 1].plot(df["t_min"], df["ullage_volume_m3"], color="tab:orange")
    axes[0, 1].set_ylabel("Ullage volume (m³)"); axes[0, 1].set_title("Ullage volume vs time")

    axes[1, 0].plot(df["t_min"], df["tank_pressure_Pa"] / 1000.0, color="tab:green")
    axes[1, 0].set_ylabel("Tank pressure (kPa)"); axes[1, 0].set_title("Tank pressure vs time")

    axes[1, 1].plot(df["t_min"], df["tank_temperature_K"] - 273.15, color="tab:red")
    axes[1, 1].set_ylabel("Tank temperature (°C)"); axes[1, 1].set_title("Temperature vs time")

    axes[2, 0].plot(df["t_min"], df["o2_fraction"] * 100.0, color="tab:purple")
    axes[2, 0].axhline(12.0, color="gray", linestyle="--", linewidth=1, label="target 12%")
    axes[2, 0].set_ylabel("Ullage O₂ (%)"); axes[2, 0].set_xlabel("Time (min)")
    axes[2, 0].set_title("O₂ concentration vs time"); axes[2, 0].legend()

    axes[2, 1].plot(df["t_min"], df["inert_flow_mol_s"], color="tab:brown")
    axes[2, 1].set_ylabel("Inert gas flow (mol/s)"); axes[2, 1].set_xlabel("Time (min)")
    axes[2, 1].set_title("Inert-gas flow vs time")

    fig.tight_layout()
    if save_path:
        fig.savefig(save_path, dpi=150)
    return fig