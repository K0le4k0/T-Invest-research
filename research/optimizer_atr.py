import sys
import pandas as pd
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]

sys.path.append(str(ROOT_DIR))

from strategies.liquid_momentum.backtest import run_strategy

from strategies.liquid_momentum.config import CONFIG

results = []

for atr_multiplier in [
    3.5,
    3.75,
    4.0,
    4.25,
    4.5,
]:

    config = CONFIG.copy()

    config["max_positions"] = 1
    config["top_n"] = 2
    config["atr_multiplier"] = atr_multiplier

    print()
    print(f"TEST atr_multiplier={atr_multiplier}")

    metrics, _, _ = run_strategy(config)

    results.append(
        {
            "atr_multiplier": config["atr_multiplier"],
            "total_return": metrics["Total Return"],
            "cagr": metrics["CAGR"],
            "profit_factor": metrics["Profit Factor"],
            "winrate": metrics["Winrate"],
            "max_drawdown": metrics["Max Drawdown"],
            "sharpe": metrics["Sharpe"],
        }
    )

print()
print("========== RESULTS ==========")

for row in results:

    print(row)

results_df = pd.DataFrame(results)

results_df = results_df.sort_values(
    "total_return",
    ascending=False,
)

results_df.to_csv(
    "results/optimization_results_atr.csv",
    index=False,
)

print()
print("Saved: results/optimization_results_atr.csv")
print()
print(results_df.head(10))
