import sys
import pandas as pd
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]

sys.path.append(str(ROOT_DIR))

from strategies.liquid_momentum.backtest import run_strategy

from strategies.liquid_momentum.config import CONFIG

results = []

for top_n in range(1, 11):

    config = CONFIG.copy()

    config["max_positions"] = 1
    config["top_n"] = top_n

    print()
    print(f"TEST top_n={top_n}")

    metrics, _, _ = run_strategy(config)

    results.append(
        {
            "top_n": top_n,
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
    "results/optimization_results.csv",
    index=False,
)

print()
print("Saved: results/optimization_results.csv")
print()
print(results_df.head(10))
