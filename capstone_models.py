"""
QM 2023 Capstone - Milestone 3 Econometric Models

This script implements:
1) Model A: Fixed-effects panel model with required diagnostics and robustness checks.
2) Model B Option 2: ARIMA forecast (with auto_arima order selection).
3) Model B Option 3: OLS vs Random Forest predictive comparison.

Outputs are written to:
- results/tables/M3_*.csv
- results/figures/M3_*.png
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import statsmodels.api as sm

from linearmodels.panel import PanelOLS
from pmdarima import auto_arima
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
from statsmodels.stats.diagnostic import het_breuschpagan
from statsmodels.stats.outliers_influence import variance_inflation_factor
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.stattools import adfuller
from scipy import stats

# Allow importing config_paths.py from code/
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT / "code"))
from config_paths import FINAL_DATA_DIR, FIGURES_DIR, TABLES_DIR  # noqa: E402  # type: ignore[import-not-found]


SEED = 42
np.random.seed(SEED)


def stars(p: float) -> str:
    if p < 0.01:
        return "***"
    if p < 0.05:
        return "**"
    if p < 0.10:
        return "*"
    return ""


def save_regression_comparison_table(
    models: Dict[str, object],
    file_path: Path,
    notes: Dict[str, Dict[str, str]],
) -> pd.DataFrame:
    """Build a publication-style side-by-side coefficient table."""
    all_vars: List[str] = sorted(
        set().union(*[set(m.params.index.tolist()) for m in models.values()])
    )

    rows: List[Dict[str, str]] = []
    for var in all_vars:
        row_coef: Dict[str, str] = {"Variable": var}
        row_se: Dict[str, str] = {"Variable": "(SE)"}

        for model_name, result in models.items():
            if var in result.params.index:
                coef = result.params[var]
                pval = result.pvalues[var]
                se = result.std_errors[var]
                row_coef[model_name] = f"{coef:.4f}{stars(float(pval))}"
                row_se[model_name] = f"({se:.4f})"
            else:
                row_coef[model_name] = ""
                row_se[model_name] = ""

        rows.append(row_coef)
        rows.append(row_se)

    summary_rows = []
    for metric in ["N", "R2_within", "Entity_FE", "Time_FE", "Clustered_SE"]:
        metric_row = {"Variable": metric}
        for model_name, result in models.items():
            if metric == "N":
                metric_row[model_name] = f"{int(result.nobs)}"
            elif metric == "R2_within":
                metric_row[model_name] = f"{float(result.rsquared_within):.4f}"
            else:
                metric_row[model_name] = notes[model_name][metric]
        summary_rows.append(metric_row)

    out = pd.DataFrame(rows + summary_rows)
    out.to_csv(file_path, index=False)
    return out


def fit_panel_model(
    panel_df: pd.DataFrame,
    y_col: str,
    x_cols: List[str],
    clustered: bool,
) -> object:
    """Fit PanelOLS with entity and time FE."""
    y = panel_df[y_col]
    x = panel_df[x_cols]

    model = PanelOLS(y, x, entity_effects=True, time_effects=True, drop_absorbed=True)
    if clustered:
        result = model.fit(cov_type="clustered", cluster_entity=True)
    else:
        result = model.fit(cov_type="unadjusted")
    return result


def run_model_a_and_diagnostics(df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
    """Run fixed effects model, diagnostics, and robustness checks."""
    out_tables: Dict[str, pd.DataFrame] = {}

    # Baseline panel setup
    panel = df.copy()
    panel["fips"] = panel["fips"].astype(str).str.zfill(5)
    panel = panel.sort_values(["fips", "year"])

    panel["log_total_damage_l1"] = panel.groupby("fips")["log_total_damage"].shift(1)
    panel["event_count_l1"] = panel.groupby("fips")["event_count"].shift(1)
    panel["log_total_damage_l2"] = panel.groupby("fips")["log_total_damage"].shift(2)
    panel["event_count_l2"] = panel.groupby("fips")["event_count"].shift(2)
    panel["log_total_damage_l3"] = panel.groupby("fips")["log_total_damage"].shift(3)
    panel["event_count_l3"] = panel.groupby("fips")["event_count"].shift(3)

    y_col = "yoy_real"
    x_base = [
        "log_total_damage_l1",
        "event_count_l1",
        "mortgage_rate_30yr",
        "unemployment_rate",
    ]

    panel_base = panel[["fips", "year", y_col] + x_base].dropna().set_index(["fips", "year"])

    model_fe_standard = fit_panel_model(panel_base, y_col, x_base, clustered=False)
    model_fe_clustered = fit_panel_model(panel_base, y_col, x_base, clustered=True)

    # Robustness check: outlier period exclusions
    panel_no_crisis = panel[(~panel["year"].between(2008, 2009)) & (panel["year"] != 2020)].copy()
    panel_no_crisis = (
        panel_no_crisis[["fips", "year", y_col] + x_base]
        .dropna()
        .set_index(["fips", "year"])
    )
    model_fe_no_crisis = fit_panel_model(panel_no_crisis, y_col, x_base, clustered=True)

    # Robustness check: alternative lag structures
    lag_results: List[Dict[str, float]] = []
    for lag in [1, 2, 3]:
        dmg_col = f"log_total_damage_l{lag}"
        evt_col = f"event_count_l{lag}"
        x_lag = [dmg_col, evt_col, "mortgage_rate_30yr", "unemployment_rate"]
        panel_lag = panel[["fips", "year", y_col] + x_lag].dropna().set_index(["fips", "year"])

        lag_fit = fit_panel_model(panel_lag, y_col, x_lag, clustered=True)
        lag_results.append(
            {
                "lag": lag,
                "coef_log_total_damage": float(lag_fit.params.get(dmg_col, np.nan)),
                "pval_log_total_damage": float(lag_fit.pvalues.get(dmg_col, np.nan)),
                "coef_event_count": float(lag_fit.params.get(evt_col, np.nan)),
                "pval_event_count": float(lag_fit.pvalues.get(evt_col, np.nan)),
                "nobs": int(lag_fit.nobs),
                "r2_within": float(lag_fit.rsquared_within),
            }
        )

    lag_df = pd.DataFrame(lag_results)
    lag_df.to_csv(TABLES_DIR / "M3_robustness_alt_lags.csv", index=False)
    out_tables["alt_lags"] = lag_df

    # Robustness check: coefficient stability summary
    robust_compare = pd.DataFrame(
        {
            "specification": [
                "FE_standard_SE",
                "FE_clustered_SE",
                "FE_clustered_SE_excl_2008_2009_2020",
            ],
            "coef_log_total_damage_l1": [
                float(model_fe_standard.params.get("log_total_damage_l1", np.nan)),
                float(model_fe_clustered.params.get("log_total_damage_l1", np.nan)),
                float(model_fe_no_crisis.params.get("log_total_damage_l1", np.nan)),
            ],
            "pval_log_total_damage_l1": [
                float(model_fe_standard.pvalues.get("log_total_damage_l1", np.nan)),
                float(model_fe_clustered.pvalues.get("log_total_damage_l1", np.nan)),
                float(model_fe_no_crisis.pvalues.get("log_total_damage_l1", np.nan)),
            ],
            "coef_event_count_l1": [
                float(model_fe_standard.params.get("event_count_l1", np.nan)),
                float(model_fe_clustered.params.get("event_count_l1", np.nan)),
                float(model_fe_no_crisis.params.get("event_count_l1", np.nan)),
            ],
            "pval_event_count_l1": [
                float(model_fe_standard.pvalues.get("event_count_l1", np.nan)),
                float(model_fe_clustered.pvalues.get("event_count_l1", np.nan)),
                float(model_fe_no_crisis.pvalues.get("event_count_l1", np.nan)),
            ],
            "nobs": [
                int(model_fe_standard.nobs),
                int(model_fe_clustered.nobs),
                int(model_fe_no_crisis.nobs),
            ],
            "r2_within": [
                float(model_fe_standard.rsquared_within),
                float(model_fe_clustered.rsquared_within),
                float(model_fe_no_crisis.rsquared_within),
            ],
        }
    )
    robust_compare.to_csv(TABLES_DIR / "M3_robustness_summary.csv", index=False)
    out_tables["robustness_summary"] = robust_compare

    # Regression table (publication-style CSV)
    reg_table = save_regression_comparison_table(
        models={
            "Model_1_FE_StandardSE": model_fe_standard,
            "Model_2_FE_ClusteredSE": model_fe_clustered,
            "Model_3_FE_ClusteredSE_NoCrisis": model_fe_no_crisis,
        },
        file_path=TABLES_DIR / "M3_regression_table.csv",
        notes={
            "Model_1_FE_StandardSE": {
                "Entity_FE": "Yes",
                "Time_FE": "Yes",
                "Clustered_SE": "No",
            },
            "Model_2_FE_ClusteredSE": {
                "Entity_FE": "Yes",
                "Time_FE": "Yes",
                "Clustered_SE": "Yes",
            },
            "Model_3_FE_ClusteredSE_NoCrisis": {
                "Entity_FE": "Yes",
                "Time_FE": "Yes",
                "Clustered_SE": "Yes",
            },
        },
    )
    out_tables["regression_table"] = reg_table

    # Diagnostics: Breusch-Pagan (proxy with pooled OLS exog matrix)
    resid = model_fe_clustered.resids.values
    exog_bp = sm.add_constant(panel_base[x_base].values)
    bp_stat, bp_pvalue, f_stat, f_pvalue = het_breuschpagan(resid, exog_bp)
    bp_df = pd.DataFrame(
        {
            "bp_stat": [bp_stat],
            "bp_pvalue": [bp_pvalue],
            "f_stat": [f_stat],
            "f_pvalue": [f_pvalue],
        }
    )
    bp_df.to_csv(TABLES_DIR / "M3_diagnostic_breusch_pagan.csv", index=False)
    out_tables["breusch_pagan"] = bp_df

    # Diagnostics: VIF
    vif_x = panel_base[x_base].copy()
    vif_data = pd.DataFrame({"Variable": vif_x.columns})
    vif_data["VIF"] = [variance_inflation_factor(vif_x.values, i) for i in range(vif_x.shape[1])]
    vif_data.to_csv(TABLES_DIR / "M3_diagnostic_vif.csv", index=False)
    out_tables["vif"] = vif_data

    # Diagnostics: Residuals vs Fitted
    fitted = model_fe_clustered.fitted_values
    if isinstance(fitted, pd.DataFrame):
        fitted_series = fitted.iloc[:, 0]
    else:
        fitted_series = pd.Series(fitted)

    plt.figure(figsize=(10, 6))
    plt.scatter(fitted_series.values, resid, alpha=0.3)
    plt.axhline(0, color="red", linestyle="--")
    plt.xlabel("Fitted Values")
    plt.ylabel("Residuals")
    plt.title("Residuals vs Fitted Values (Fixed Effects Model)")
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "M3_residuals_vs_fitted.png", dpi=300)
    plt.close()

    # Diagnostics: Q-Q plot
    plt.figure(figsize=(8, 6))
    stats.probplot(resid, dist="norm", plot=plt)
    plt.title("Q-Q Plot: Residual Normality Check")
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "M3_qq_plot.png", dpi=300)
    plt.close()

    return out_tables


def run_arima_option(df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
    """Option 2: ARIMA forecasting with auto_arima, ADF, and naive comparison."""
    out_tables: Dict[str, pd.DataFrame] = {}

    ts = (
        df.groupby("year", as_index=False)["yoy_real"]
        .mean()
        .sort_values("year")
        .set_index("year")
    )
    y = ts["yoy_real"]

    # Stationarity diagnostics
    adf_stat, adf_pvalue, _, _, crit_vals, _ = adfuller(y.dropna())
    adf_df = pd.DataFrame(
        {
            "adf_stat": [adf_stat],
            "adf_pvalue": [adf_pvalue],
            "crit_1pct": [crit_vals["1%"]],
            "crit_5pct": [crit_vals["5%"]],
            "crit_10pct": [crit_vals["10%"]],
        }
    )
    adf_df.to_csv(TABLES_DIR / "M3_arima_adf_test.csv", index=False)
    out_tables["adf"] = adf_df

    # Backtest (12-step holdout) vs naive baseline
    n_forecast = 12
    train = y.iloc[:-n_forecast]
    test = y.iloc[-n_forecast:]

    arima_selector = auto_arima(
        train,
        seasonal=False,
        stepwise=True,
        suppress_warnings=True,
        error_action="ignore",
        max_p=5,
        max_q=5,
        max_d=2,
    )
    order = arima_selector.order

    model_bt = ARIMA(train, order=order).fit()
    fc_bt = model_bt.get_forecast(steps=n_forecast)
    pred_bt = fc_bt.predicted_mean

    naive_pred = np.repeat(train.iloc[-1], n_forecast)

    rmse_arima = np.sqrt(mean_squared_error(test, pred_bt))
    rmse_naive = np.sqrt(mean_squared_error(test, naive_pred))

    # Guard against near-zero variance in small holdout windows
    try:
        r2_arima = r2_score(test, pred_bt)
    except Exception:
        r2_arima = np.nan

    try:
        r2_naive = r2_score(test, naive_pred)
    except Exception:
        r2_naive = np.nan

    acc_df = pd.DataFrame(
        {
            "model": ["ARIMA", "Naive_no_change"],
            "order": [str(order), "N/A"],
            "rmse": [rmse_arima, rmse_naive],
            "r2": [r2_arima, r2_naive],
        }
    )
    acc_df.to_csv(TABLES_DIR / "M3_arima_accuracy_vs_naive.csv", index=False)
    out_tables["arima_accuracy"] = acc_df

    # Fit full-sample ARIMA and forecast 12 periods with 95% CI
    model_full = ARIMA(y, order=order).fit()
    fc_full = model_full.get_forecast(steps=n_forecast)
    pred_mean = fc_full.predicted_mean
    conf_int = fc_full.conf_int(alpha=0.05)

    future_years = np.arange(int(y.index.max()) + 1, int(y.index.max()) + n_forecast + 1)
    forecast_df = pd.DataFrame(
        {
            "year": future_years,
            "forecast_yoy_real": pred_mean.values,
            "ci_lower_95": conf_int.iloc[:, 0].values,
            "ci_upper_95": conf_int.iloc[:, 1].values,
            "selected_order": [str(order)] * n_forecast,
        }
    )
    forecast_df.to_csv(TABLES_DIR / "M3_arima_forecast_12_steps.csv", index=False)
    out_tables["arima_forecast"] = forecast_df

    # Forecast plot
    plt.figure(figsize=(11, 6))
    plt.plot(y.index, y.values, label="Historical yoy_real", linewidth=2)
    plt.plot(future_years, pred_mean.values, label="ARIMA forecast", linestyle="--")
    plt.fill_between(
        future_years,
        conf_int.iloc[:, 0].values,
        conf_int.iloc[:, 1].values,
        alpha=0.2,
        label="95% confidence band",
    )
    plt.xlabel("Year")
    plt.ylabel("YoY Real HPI Growth (%)")
    plt.title("ARIMA 12-Step Forecast for National Real HPI Growth")
    plt.legend()
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "M3_arima_forecast.png", dpi=300)
    plt.close()

    return out_tables


def run_ml_option(df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
    """Option 3: Compare OLS vs RandomForest on annual aggregate prediction."""
    out_tables: Dict[str, pd.DataFrame] = {}

    annual = (
        df.groupby("year", as_index=False)
        .agg(
            yoy_real=("yoy_real", "mean"),
            total_damage=("total_damage", "sum"),
            event_count=("event_count", "sum"),
            total_injuries=("total_injuries", "sum"),
            mortgage_rate_30yr=("mortgage_rate_30yr", "mean"),
            unemployment_rate=("unemployment_rate", "mean"),
            fed_funds_rate=("fed_funds_rate", "mean"),
            treasury_10yr=("treasury_10yr", "mean"),
        )
        .sort_values("year")
    )

    annual["log_total_damage"] = np.log1p(annual["total_damage"])

    features = [
        "log_total_damage",
        "event_count",
        "total_injuries",
        "mortgage_rate_30yr",
        "unemployment_rate",
        "fed_funds_rate",
        "treasury_10yr",
    ]

    model_df = annual[["year", "yoy_real"] + features].dropna().copy()

    # Time-ordered train/test split
    split_idx = int(len(model_df) * 0.8)
    train_df = model_df.iloc[:split_idx]
    test_df = model_df.iloc[split_idx:]

    x_train = train_df[features]
    y_train = train_df["yoy_real"]
    x_test = test_df[features]
    y_test = test_df["yoy_real"]

    # OLS
    x_train_const = sm.add_constant(x_train)
    x_test_const = sm.add_constant(x_test, has_constant="add")
    ols_fit = sm.OLS(y_train, x_train_const).fit()
    ols_pred = ols_fit.predict(x_test_const)

    # Random Forest
    rf = RandomForestRegressor(
        n_estimators=500,
        max_depth=5,
        random_state=SEED,
    )
    rf.fit(x_train, y_train)
    rf_pred = rf.predict(x_test)

    # Metrics
    ml_compare = pd.DataFrame(
        {
            "model": ["OLS", "RandomForest"],
            "test_r2": [r2_score(y_test, ols_pred), r2_score(y_test, rf_pred)],
            "test_rmse": [
                np.sqrt(mean_squared_error(y_test, ols_pred)),
                np.sqrt(mean_squared_error(y_test, rf_pred)),
            ],
        }
    )
    ml_compare.to_csv(TABLES_DIR / "M3_ml_model_comparison.csv", index=False)
    out_tables["ml_comparison"] = ml_compare

    rf_importance = pd.DataFrame(
        {
            "feature": features,
            "importance": rf.feature_importances_,
        }
    ).sort_values("importance", ascending=False)
    rf_importance.to_csv(TABLES_DIR / "M3_rf_feature_importance.csv", index=False)
    out_tables["rf_importance"] = rf_importance

    ols_coef = pd.DataFrame(
        {
            "term": ols_fit.params.index,
            "coef": ols_fit.params.values,
            "std_err": ols_fit.bse.values,
            "p_value": ols_fit.pvalues.values,
        }
    )
    ols_coef.to_csv(TABLES_DIR / "M3_ols_coefficients.csv", index=False)
    out_tables["ols_coef"] = ols_coef

    # Prediction scatter plot
    plt.figure(figsize=(8, 6))
    plt.scatter(y_test, ols_pred, alpha=0.7, label="OLS")
    plt.scatter(y_test, rf_pred, alpha=0.7, label="RandomForest")
    min_v = min(float(y_test.min()), float(ols_pred.min()), float(np.min(rf_pred)))
    max_v = max(float(y_test.max()), float(ols_pred.max()), float(np.max(rf_pred)))
    plt.plot([min_v, max_v], [min_v, max_v], linestyle="--", color="black", linewidth=1)
    plt.xlabel("Actual yoy_real")
    plt.ylabel("Predicted yoy_real")
    plt.title("Test-Set Predictions: OLS vs Random Forest")
    plt.legend()
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "M3_ml_predictions_comparison.png", dpi=300)
    plt.close()

    return out_tables


def main() -> None:
    TABLES_DIR.mkdir(parents=True, exist_ok=True)
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    data_path = FINAL_DATA_DIR / "housing_disasters_panel.csv"
    df = pd.read_csv(data_path)

    model_a_outputs = run_model_a_and_diagnostics(df)
    arima_outputs = run_arima_option(df)
    ml_outputs = run_ml_option(df)

    # Master output index for easy grading/review
    output_index = pd.DataFrame(
        {
            "output_type": ["table"] * (len(model_a_outputs) + len(arima_outputs) + len(ml_outputs)),
            "name": list(model_a_outputs.keys()) + list(arima_outputs.keys()) + list(ml_outputs.keys()),
        }
    )
    output_index.to_csv(TABLES_DIR / "M3_output_index.csv", index=False)

    print("M3 pipeline completed successfully.")
    print(f"Tables saved to: {TABLES_DIR}")
    print(f"Figures saved to: {FIGURES_DIR}")


if __name__ == "__main__":
    main()
