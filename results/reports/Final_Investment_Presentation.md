# How do repeated natural disasters affect local housing price growth and volatility in high-risk counties?

**Team:** Brice, Ricky, Zach  
**Course:** QM 2023: Statistics II / Data Analytics  
**Date:** April 30, 2026

---

## Slide 1: Executive Summary
- No meaningful disaster-price penalty found in the county panel.
- Macro-financing conditions (mortgage rates, Treasury yields) are stronger drivers of housing price growth.
- Recommendation: Use disaster history as a secondary risk screen; focus on rate-sensitive markets.

---

## Slide 2: Methodology
- Data Sources:
  - NOAA Storm Events (county-level disaster exposure)
  - Yale/Shiller home price series (real housing price growth)
  - FRED (national macro controls)
- Panel: 116,137 rows, 3,347 counties, 1980-2022
- Main Model: Two-way fixed effects with county-clustered SEs
- Key Variables: yoy_real, log_total_damage_l1, event_count_l1, mortgage_rate_30yr, unemployment_rate, fed_funds_rate, treasury_10yr

---

## Slide 3: Results (Main Model)
- Table 1: Main Fixed-Effects Regression
  - Disaster coefficients: Effectively zero, not significant
  - County and year effects control for confounders
- Robustness Checks: Results stable across SE choices, lag structures, and crisis-period exclusions

---

## Slide 4: Results (Alternative Models)
- Table 2: Alternative Models
  - ARIMA outperforms naive forecast
  - Random forest slightly better than OLS, but limited predictive power
- Figure 1: Lag Sensitivity of Housing Growth to Mortgage Rates (show plot)
- Figure 2: Residual Diagnostics (show plot)

---

## Slide 5: Conclusions & Recommendations
- Focus on rate-aware allocation, not disaster-driven strategy
- Prioritize markets with strong fundamentals and low rate exposure
- Disaster risk matters for insurance/resilience, but not main pricing driver in this panel
- Main caveat: Limited local variation, possible omitted variables, external validity concerns

---

## Slide 6: References & AI Audit
- FRED, NOAA Storm Events, Shiller Home Price Data
- Copilot used for code, analysis, and memo drafting
- All results verified against exported tables/figures

---

## Slide 7: Q&A
- Questions?
