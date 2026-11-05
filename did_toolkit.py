"""Difference-in-differences toolkit (ECON 5200 PS3), extending Lab 11's did_utils.py."""
from __future__ import annotations

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
import statsmodels.api as sm

# Lab 11's functions, carried over
def two_by_two(df: pd.DataFrame, outcome: str, treated: str, post: str) -> float:
    """Calculate the difference in differences."""
    g = df.groupby([treated, post])[outcome].mean()
    return (g[1, 1] - g[1, 0]) - (g[0, 1] - g[0, 0])

def event_study(cells: pd.DataFrame) -> pd.DataFrame:
    """Average the effects at each event time."""
    rows = []

    for e, group in cells.groupby("e"):
        effect = np.average(group["att"], weights=group["n"])
        rows.append({"e": e, "att": effect})

    return pd.DataFrame(rows)

def clean_att(df: pd.DataFrame) -> tuple:
    """Estimate effects using only untreated controls."""
    rows = []

    for g in sorted(df.loc[df["g"] < 10**9, "g"].unique()):
        treated = df[df["g"] == g]
        baseline = g - 1

        for year in range(g, df["year"].max() + 1):
            controls = df[df["g"] > year]

            if controls.empty:
                continue

            treated_change = (
                treated.loc[treated["year"] == year, "y"].mean()
                - treated.loc[treated["year"] == baseline, "y"].mean()
            )

            control_change = (
                controls.loc[controls["year"] == year, "y"].mean()
                - controls.loc[controls["year"] == baseline, "y"].mean()
            )

            rows.append({
                "g": g,
                "year": year,
                "e": year - g,
                "att": treated_change - control_change,
                "n": (treated["year"] == year).sum()
            })

    cells = pd.DataFrame(rows)
    average_att = np.average(cells["att"], weights=cells["n"])

    return cells, average_att

# your clustered-inference wrapper (Step 3.3)

def clustered_inference(df: pd.DataFrame) -> dict:
    """Fit TWFE with default, county and board standard errors."""
    formula = "y ~ D + C(county) + C(year)"

    default = smf.ols(formula, data=df).fit()

    county = smf.ols(formula, data=df).fit(
        cov_type="cluster", cov_kwds={"groups": df["county"]}
    )

    board = smf.ols(formula, data=df).fit(
        cov_type="cluster", cov_kwds={"groups": df["board"]}
    )

    return {"Default": default, "County": county, "Board": board}

# your bootstrap (Task 4.1)
# your bootstrap (Task 4.1)

def wild_cluster_bootstrap(panel: pd.DataFrame, cluster: str) -> float:
    """Calculate the bootstrap p-value using all 256 board signs."""
    data = panel.dropna(
        subset=["y", "D", "county", "year", cluster]
    ).copy()

    board_numbers, boards = pd.factorize(data[cluster])

    if len(boards) != 8:
        raise ValueError("This test needs eight boards.")

    model = smf.ols("y ~ D + C(county) + C(year)", data=data)
    actual = model.fit(
        cov_type="cluster",
        cov_kwds={"groups": board_numbers}
    )

    X = model.exog
    d_position = model.exog_names.index("D")
    actual_t = actual.tvalues["D"]

    # Fit the model with the treatment effect set to zero
    X_restricted = np.delete(X, d_position, axis=1)
    restricted = sm.OLS(data["y"].to_numpy(), X_restricted).fit()

    fitted = np.asarray(restricted.fittedvalues)
    residuals = np.asarray(restricted.resid)
    bootstrap_t = []

    for number in range(256):
        weights = np.ones(8)

        for board in range(8):
            if (number >> board) & 1:
                weights[board] = -1

        # Everyone in a board gets the same sign
        y_star = fitted + weights[board_numbers] * residuals

        result = sm.OLS(y_star, X).fit(
            cov_type="cluster",
            cov_kwds={"groups": board_numbers}
        )

        bootstrap_t.append(result.tvalues[d_position])

    bootstrap_t = np.array(bootstrap_t)
    extreme = np.abs(bootstrap_t) >= abs(actual_t) - 1e-10

    return float(extreme.mean())


if __name__ == "__main__":
    example = pd.DataFrame({
        "treated": [0, 0, 1, 1],
        "post": [0, 1, 0, 1],
        "y": [1, 2, 1, 5]
    })

    assert two_by_two(example, "y", "treated", "post") == 3

    example_cells = pd.DataFrame({
        "e": [0, 0, 1],
        "att": [2, 4, 6],
        "n": [1, 3, 1]
    })

    result = event_study(example_cells)

    assert result.loc[result["e"] == 0, "att"].iloc[0] == 3.5
    assert result.loc[result["e"] == 1, "att"].iloc[0] == 6

    print("All checks passed.")

if __name__ == "__main__":
    ...   # passing assertions
