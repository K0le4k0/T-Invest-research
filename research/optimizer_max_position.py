import sys
import pandas as pd
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]

sys.path.append(str(ROOT_DIR))

from strategies.liquid_momentum.backtest import run_strategy

from strategies.liquid_momentum.config import CONFIG

results = []

for max_positions in range(1, 8):

    config = CONFIG.copy()

    config["top_n"] = 2
    config["max_positions"] = max_positions

    print()
    print(f"TEST max_positions={max_positions}")

    metrics, _, _ = run_strategy(config)

    results.append(
        {
            "max_positions": max_positions,
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
    "results/optimization_max_positions.csv",
    index=False,
)

print()
print(results_df)

print()
print("Saved: results/optimization_max_positions.csv")
