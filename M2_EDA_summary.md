# M2 EDA Summary

## Key Findings

- Interest-rate exposure is a dominant pattern: county-year real housing growth (`yoy_real`) is negatively correlated with `mortgage_rate_30yr` (r = -0.433), `fed_funds_rate` (r = -0.412), and `treasury_10yr` (r = -0.423). Economic mechanism: higher rates raise borrowing costs and lower housing affordability, reducing demand and price growth.
- Lag analysis suggests a near-contemporaneous transmission channel: annual average `yoy_real` has the strongest correlation with mortgage rates at lag 0 (r = -0.479), with weaker links as lag increases (lag 1: -0.388, lag 2: -0.268). Mechanism: mortgage payment sensitivity affects transaction volume and pricing quickly.
- Regional group sensitivity is substantial and policy-relevant: sensitivity of `yoy_real` to `mortgage_rate_30yr` is below -0.3 in Midwest (-0.458), South (-0.430), West (-0.389), and Northeast (-0.386). Mechanism: differences in leverage, rebuilding friction, insurance markets, and migration pressure likely drive heterogeneous pass-through.
- Outlier macro periods materially affect trends: the annual mean `yoy_real` has extreme values in 2005 (+6.79%) and 2008 (-15.45%). Mechanism: pre-crisis credit expansion and subsequent financial-crisis correction dominate broad housing dynamics.
- Control-variable scatter patterns indicate omitted-variable risk if unmodeled: `unemployment_rate` and `treasury_10yr` both show negative bivariate slopes with `yoy_real`, consistent with macro-demand and discount-rate channels.

## Hypotheses for M3

### Hypothesis 1 (Driver Effect)

- Claim: Higher disaster exposure is associated with lower county housing price growth.
- Suggested model specification:
  - `yoy_real_it = beta1 * log_total_damage_it + beta2 * event_count_it + gamma * X_t + alpha_i + delta_t + epsilon_it`
- Expected sign:
  - `beta1 < 0`, `beta2 < 0`
- Economic mechanism:
  - Repeated shocks increase expected repair costs and risk premia, reducing buyers' willingness to pay and slowing appreciation.

### Hypothesis 2 (Control Premiums / Macro Channels)

- Claim: Financing and macro conditions independently shape housing growth.
- Suggested model specification:
  - `yoy_real_it = beta * disaster_it + theta1 * mortgage_rate_30yr_t + theta2 * unemployment_rate_t + theta3 * treasury_10yr_t + alpha_i + delta_t + epsilon_it`
- Expected sign:
  - `theta1 < 0`, `theta2 < 0`, `theta3 < 0`
- Economic mechanism:
  - Higher rates reduce affordability; higher unemployment weakens demand and credit quality.

### Hypothesis 3 (Group Heterogeneity)

- Claim: Rate sensitivity differs by region.
- Suggested model specification:
  - `yoy_real_it = beta * mortgage_rate_30yr_t + sum_r phi_r * (Region_ir x mortgage_rate_30yr_t) + controls + alpha_i + delta_t + epsilon_it`
- Expected sign:
  - For sensitive regions (Midwest, South, West, Northeast), `phi_r < 0` relative to omitted baseline.
- Economic mechanism:
  - Regions differ in leverage structure, insurance penetration, reconstruction constraints, and migration elasticity.

## Data Quality Flags and M3 Mitigations

- Outlier periods:
  - Flag: 2005 and 2008 strongly influence aggregate patterns.
  - Mitigation: include year fixed effects; run robustness checks excluding crisis years and using winsorized outcome tails for sensitivity tests.
- Missing values:
  - Flag: `case_shiller_national` (~12.1%) and `case_shiller_national_yoy` (~13.9%) are missing pre-1987 by construction.
  - Mitigation: avoid these series in baseline 1980-1986 specs or use sample-restricted checks when included.
- Heteroskedasticity risk:
  - Flag: damage and growth distributions are heavy-tailed across counties.
  - Mitigation: use heteroskedasticity-robust (HC) or county-clustered standard errors; retain log transforms for skewed disaster variables.
- Multicollinearity among rate controls:
  - Flag: very high pairwise correlations (`mortgage_rate_30yr` vs `treasury_10yr`: 0.994; `fed_funds_rate` vs `mortgage_rate_30yr`: 0.950).
  - Mitigation: avoid including highly collinear rate series simultaneously in the same specification; estimate alternative control sets and report variance-inflation diagnostics.
- Selection/composition risk from disaster panel construction:
  - Flag: panel is event-derived and may underrepresent zero-event county-years without an external complete county-year frame.
  - Mitigation: in M3 robustness, merge to a full county-year backbone (Census FIPS panel) and code zero-event observations explicitly.
