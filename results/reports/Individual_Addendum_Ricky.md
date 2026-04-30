# Individual Addendum - Ricky

**Name:** Ricky  
**Team:** Brice, Ricky, Zach  
**Date:** May 1, 2026

---

## 1. Personal Contribution to Capstone Milestones

### Milestone 1: Data Pipeline (Week 5)
- Verified Zach's `fetch_sheldus_data.py`, `fetch_shiller_data.py`, `fetch_fred_data.py` implementations by reproducing all outputs independently
- Tested merge logic in `merge_final_panel.py`: confirmed 0 duplicate (fips, year) pairs, checked for data loss at merge boundaries, verified no rows dropped unexpectedly
- Completed M1 assignment documentation: wrote `M1_data_quality_report.md` (6 sections: data sources, cleaning decisions with before/after counts, merge verification, summary statistics, reproducibility checklist, ethical considerations)
- Contributed to `AI_AUDIT_APPENDIX.md`: documented AI use across M1 with disclose/verify/critique framework
- Updated `data/final/data_dictionary.md`: fixed 4 variables with "Unknown" source; corrected SHELDUS labels to NOAA Storm Events
- Hours: 18 hours
- Key deliverable: `M1_data_quality_report.md`, `AI_AUDIT_APPENDIX.md` (M1 section), data dictionary verification

### Milestone 2: EDA Dashboard (Week 10)
- Wrote M2 narrative findings and economic interpretations: translated correlation results into hypothesis language
- Created `M2_EDA_summary.md`: documented key findings (interest-rate dominance, lag sensitivity, regional heterogeneity), formulated 3 hypotheses for M3, identified data quality flags and mitigations
- Conducted group sensitivity analysis: computed correlation of yoy_real with mortgage_rate_30yr by region, flagged Midwest, South, West as sensitive (r < -0.3), motivated group × driver interactions for M3
- Generated captions and interpretations for all 8 visualizations (plots 1–8)
- Hours: 14 hours
- Key deliverable: `M2_EDA_summary.md`, visualization captions, group sensitivity analysis

### Milestone 3: Econometric Models (Week 12)
- Wrote `M3_interpretation.md`: interpreted Model A results in economic units and p-values; explained heteroskedasticity diagnosis and rationale for clustered SEs; summarized Models B (ARIMA, ML comparison)
- Ran and interpreted diagnostic tests: explained Breusch-Pagan heteroskedasticity result (p < 0.001), VIF multicollinearity findings (max VIF 7.79 for unemployment_rate), residual plots
- Synthesized robustness checks: documented coefficient stability across ARIMA standard vs. clustered SE, alternative lag structures, crisis-period exclusion; explained why null result persists robustly
- Updated `AI_AUDIT_APPENDIX.md` (M2 and M3 sections): documented AI use with verification and critique for EDA and modeling tasks
- Hours: 16 hours
- Key deliverable: `M3_interpretation.md`, `AI_AUDIT_APPENDIX.md` (M2 and M3 sections), diagnostic interpretation

### Milestone 4: Final Investment Memo (Week 14)
- Drafted Methodology section: clearly stated two-way FE specification, explained county and year fixed effects, justified lagged disaster variables, documented Model B choices (ARIMA and ML)
- Drafted Conclusions & Recommendations section: translated null FE results into business language; provided honest caveats (identification limits, omitted variables, external validity concerns)
- Edited full memo for clarity: removed jargon, simplified econometric language for non-technical audience, ensured all tables and figures were properly referenced
- Hours: 10 hours
- Key deliverable: Methodology and Conclusions sections of Final_Investment_Memo.md; full editorial pass

**Total Hours:** 58 hours

---

## 2. One Defended Methodological Decision

**Decision:** Prioritize the clustered standard error (CSE) specification as the primary inference result rather than standard unadjusted SEs, despite similar coefficients

**Reasoning:**
- Evidence: M3 Breusch-Pagan test shows strong evidence of heteroskedasticity (p < 0.001). Standard errors from unadjusted Var-Cov are downward-biased when this violation exists.
- Economic justification: Housing returns, disaster damage, and macro controls all have fat tails and heavy skew across counties and years. Heteroskedasticity is not just a statistical artifact—it reflects real economic dispersion (volatile rural markets, stable urban cores).
- Robustness support: M3 results show that coefficients remain identical (0.0000) and insignificant regardless of SE choice (p=0.792 standard vs. p=0.789 clustered for disaster damage; p=0.759 standard vs. p=0.715 clustered for event count). The null conclusion is robust; the SE choice affects precision, not direction.

**Alternative considered:** Using bootstrapped SEs or resampling methods
- Why not: Clustered SEs are the standard in panel econometrics and are simpler to interpret. Bootstrap was overkill for this dataset, and clustered SEs already passed robustness checks.

---

## 3. One Key Limitation of Our Analysis

**Limitation:** The M3 model assumes that unobserved county-level factors (local income trends, migration, credit availability, housing stock composition) are time-invariant, i.e., do not change between 1980 and 2022.

**Why this matters:** Many counties experienced dramatic structural changes over 40+ years (suburbanization in the 1990s, deindustrialization in the 2000s, pandemic remote work spillovers in 2020+). If these changes correlate with both disaster exposure and housing growth, county fixed effects will not block the confounding. For example, a county that lost manufacturing and became less vulnerable to disasters may appear resilient, when in fact it is just economically declining. This time-varying selection bias could mask true disaster effects.

**Potential mitigation:** Use instrumental variables (e.g., historical geological disaster risk as an IV for current exposure) to address endogeneity, or conduct subset analyses restricting to stable counties with low migration rates. Alternatively, include time-varying controls for county characteristics (median income, unemployment, population density) if external data can be linked to the panel.

---

## 4. AI Audit — Detailed Examples

### Example 1: M2 Economic Interpretation Writing
- **Prompt:** "Translate these correlations (r = -0.433 for mortgage_rate_30yr, r = -0.412 for fed_funds_rate, r = -0.423 for treasury_10yr) into plain-English hypothesis for an econometrics team. What mechanism could explain this pattern?"
- **Output:** Three hypotheses focusing on affordability, discount-rate channels, and credit conditions
- **Verification:** Cross-checked against housing economics literature (mortgage-rate sensitivity is well-established); verified coefficients were correctly transcribed; confirmed hypotheses align with M3 specification choices (lagged mortgage rates, controls for unemployment as credit proxy)
- **Critique:** AI initially suggested including Case-Shiller national HPI as a predictor, but this is circular reasoning (national HPI is part of our outcome construction). I removed that suggestion and kept focus on drivers (rates, unemployment) and identification strategy.

### Example 2: M3 Heteroskedasticity Diagnosis
- **Prompt:** "I ran a Breusch-Pagan test and got p < 0.001. What does this mean for my standard errors, and what should I do?"
- **Output:** Explanation of heteroskedasticity bias, code for clustered SE implementation
- **Verification:** Ran clustered SE model; confirmed coefficients matched unadjusted model (ruling out specification error); re-ran BP test on residual diagnostics to confirm persistence; verified VIF <10 (no collinearity)
- **Critique:** AI's initial response was overly technical. I rewrote the M3 interpretation memo to make it clearer: "We use clustered standard errors because Breusch-Pagan rejects homoskedasticity. This protects our inference when variance is unequal across counties."

### Example 3: Memo Writing - Plain English for Non-Technical Audience
- **Prompt:** "How do I rewrite this sentence for a non-economist? 'The point estimate of β₁ is economically negligible and statistically indistinguishable from zero.'"
- **Output:** "Our analysis does not find a meaningful disaster-price penalty in the current county panel."
- **Verification:** Embedded the rewritten sentence in the Executive Summary; confirmed non-technical colleagues understood the meaning without loss of precision; verified it matched the underlying statistical claim.
- **Critique:** AI's first draft said "no effect," which is too strong. I edited to say "no meaningful effect in this panel," which honestly reflects the identification limitations while communicating the main finding.

### Overall AI Use
**Estimate:** Approximately 25% of my work involved AI assistance (primarily idea generation, writing scaffolding, and technical diagnostics). Economic interpretation, hypothesis development, and all data quality assessments were independent. Memo editing for clarity drew on AI suggestions but was substantially my own voice.

**Types of help:** Writing ideas, econometric diagnostics interpretation, translation of technical to plain English
**What I verified independently:** Every economic claim and limitation statement was fact-checked against the M3 outputs and existing literature. All memo sections underwent independent editorial review for accuracy and tone.

---

## 5. Self-Reflection

### What did I do particularly well on this capstone?
I excelled at translating technical results into clear stories for different audiences. The M2 summary and M3 interpretation were my strongest work—I took complex correlations and heteroskedasticity diagnostics and made them intelligible and actionable. I also took pride in the M1 data quality documentation; doing this thoroughly early saved time and confusion in M2 and M3.

### What could I have improved?
I could have engaged more with the econometric modeling itself rather than deferring to interpretation. Sitting in on more of Zach's M3 implementation would have deepened my understanding of why certain choices (e.g., lag structure) matter. I also could have started external reading about dynamic panel models and IV strategies earlier to produce more sophisticated mitigation strategies for limitations.

### What did I learn from this capstone project?
This project taught me the power of clear documentation. Spending 18 hours on M1 documentation saved weeks of confusion later. I also learned that "no effect" results are just as publishable as "positive effects"—the key is rigorous robustness checks and honest limitation discussion. Finally, I gained confidence translating between econometric jargon and business language, a skill I know will be valuable in any data-driven career.

---

## 6. Attestation

By submitting this individual addendum, I affirm that:
- ☑ All contributions listed above are accurate and honest
- ☑ I have not exaggerated my role or minimized teammates' contributions
- ☑ I understand this addendum may be used to adjust my individual grade relative to the team grade
- ☑ I take full responsibility for my work and any errors in the sections I authored

**Signature:** _________________________________ **Date:** May 1, 2026
