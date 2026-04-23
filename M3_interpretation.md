# M3 Interpretation Memo

## Model A Headline (Fixed Effects)

A 1-unit increase in lagged log disaster damage (`log_total_damage_l1`) is associated with approximately 0.0000 percentage-point change in `yoy_real` (clustered FE estimate: 1.63e-18, p = 0.789). A 1-event increase in lagged event count (`event_count_l1`) is also associated with approximately 0.0000 percentage-point change in `yoy_real` (1.20e-18, p = 0.715).

Interpretation in economic units: in this specification, the estimated disaster effects are economically negligible and statistically insignificant.

## Economic Interpretation and Mechanisms

Expected theory channels were:

1. Damage-repair cost channel: repeated disasters should reduce local willingness-to-pay and expected appreciation.
2. Insurance-risk premium channel: repeated losses may increase insurance costs and risk premia, weakening housing demand.
3. Credit/affordability channel: tighter financing conditions can amplify price pressure in exposed areas.

However, the estimated effects are near zero in this panel setup. The main reason is a data-structure limitation: the housing outcome (`yoy_real`) is national-by-year and replicated across counties, while county variation comes from disaster variables. With both county and year fixed effects, identifying cross-county disaster effects on a national outcome is extremely weak.

## Model B Summary

This milestone includes both Option 2 and Option 3 to satisfy the Model B pathway.

### Option 2: ARIMA Forecast (12-step horizon)

- Stationarity (ADF): test reported in `results/tables/M3_arima_adf_test.csv`.
- `auto_arima` selected order: (2, 0, 0).
- Forecast file: `results/tables/M3_arima_forecast_12_steps.csv`.
- Accuracy vs naive baseline (12-step holdout):
  - ARIMA RMSE: 5.80
  - Naive no-change RMSE: 8.18

Key takeaway: historical patterns have moderate predictive content; ARIMA outperforms a no-change baseline on RMSE.

### Option 3: OLS vs Random Forest

- Test-set performance:
  - OLS: R² = -2.40, RMSE = 4.34
  - Random Forest: R² = -1.38, RMSE = 3.63
- RF improves RMSE relative to OLS but both models have low out-of-sample fit.
- Feature-importance table saved in `results/tables/M3_rf_feature_importance.csv`.

Interpretability trade-off: Random Forest improves prediction error but sacrifices coefficient-level interpretability compared with OLS.

## Diagnostics (Required)

### 1. Heteroskedasticity (Breusch-Pagan)

- File: `results/tables/M3_diagnostic_breusch_pagan.csv`
- Result: p-value < 0.001
- Interpretation: heteroskedasticity is present.
- Fix applied: clustered standard errors by county in the main FE specification.

### 2. Multicollinearity (VIF)

- File: `results/tables/M3_diagnostic_vif.csv`
- Maximum VIF: 7.79 (`unemployment_rate`), below the common threshold of 10.
- Interpretation: moderate collinearity but not at the severe cutoff.

### 3. Residual Diagnostics

- Residuals vs fitted: `results/figures/M3_residuals_vs_fitted.png`
- Q-Q plot: `results/figures/M3_qq_plot.png`

Interpretation: residuals are centered but non-normality/heavy tails are still plausible in macro-financial data. This further supports robust/clustered inference.

## Robustness Checks (Required)

Three robustness checks were completed:

1. Standard errors comparison (non-clustered vs clustered): baseline coefficients are unchanged in sign/magnitude and remain insignificant.
2. Alternative lag structures (lags 1, 2, 3): disaster coefficients remain near zero and insignificant across lag choices (`results/tables/M3_robustness_alt_lags.csv`).
3. Outlier period exclusion (2008-2009 and 2020 removed): results remain near zero and insignificant (`results/tables/M3_robustness_summary.csv`).

Conclusion on robustness: findings are stable to inference method, lag definition, and crisis-period exclusions.

## Caveats and Limitations

1. Outcome variation limitation: `yoy_real` is national and repeated across counties; with year FE, macro variation is absorbed, weakening identification of disaster effects.
2. Omitted-variable risk: county-level housing fundamentals (inventory, migration, credit conditions, local income) are not fully modeled.
3. External validity: inference is strongest for this constructed panel design and may not generalize to true county-level home-price indexes.
4. Causal interpretation caution: this FE setup addresses some confounding, but does not by itself guarantee causal identification.

## Bottom Line

In the current dataset structure, Model A does not find economically meaningful disaster effects on the national real HPI growth measure. Model B shows that time-series forecasting can beat naive baseline (ARIMA), and that nonlinear ML can slightly improve predictive RMSE over OLS, but with reduced interpretability and still-limited absolute predictive power.
