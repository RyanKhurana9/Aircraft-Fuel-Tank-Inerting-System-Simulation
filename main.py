from src.simulation import run_simulation
from src.plotting import plot_results

if __name__ == "__main__":
    df = run_simulation()
    df.to_csv("data/simulation_output.csv", index=False)
    plot_results(df, save_path="simulation_analysis.png")
    print(df.describe())