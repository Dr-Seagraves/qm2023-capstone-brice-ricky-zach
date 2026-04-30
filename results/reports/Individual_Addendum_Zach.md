# Individual Addendum - Zach

**Name:** Zach  
**Team:** Brice, Ricky, Zach  
**Date:** May 1, 2026

---

## 1. Personal Contribution to Capstone Milestones

### Milestone 1: Data Pipeline (Week 5)
- Implemented `fetch_sheldus_data.py`: auto-downloaded 65 years of NOAA Storm Events data (1.2M rows), parsed damage encoding (10K, 2.5M, 1B → float USD), aggregated to 150K county-year records
- Implemented `fetch_shiller_data.py`: fixed column position parsing to correctly read Shiller's Fig3-1.xls CPI column (column 14 vs. assumed column 2), computed real HPI by deflating with CPI
- Implemented `fetch_fred_data.py`: FRED API integration with error handling, missing value documentation
- Implemented `merge_final_panel.py`: merged all three datasets with FIPS linking logic, produced 116K row final panel with 24 columns
- Tested and verified all 4 scripts end-to-end; confirmed final panel dimensions and value ranges
- Hours: 28 hours
- Key deliverable: All four data pipeline scripts (`code/fetch_*.py` and `merge_final_panel.py`); validated 116,137-row housing_disasters_panel.csv

### Milestone 2: EDA Dashboard (Week 10)
- Built the core EDA notebook structure and lag analysis computations (tested lags 0–12 months for mortgage rate sensitivity)
- Verified correlation calculations and summary statistics across all variables
- Generated diagnostic plots used to inform M3 specification (lag sensitivity, distribution checks)
- Hours: 12 hours
- Key deliverable: Data preparation and lag analysis section of `capstone_eda.ipynb`

### Milestone 3: Econometric Models (Week 12)
- Implemented core fixed-effects panel setup: linearmodels.PanelOLS with entity and time FE, lagged variable construction
- Ran heteroskedasticity (Breusch-Pagan) test, diagnosed VIF collinearity, verified cluster configuration
- Implemented standard vs. clustered SE comparison, crisis-period exclusion robustness check, alternative lag structures (lags 1, 2, 3)
- Generated diagnostic plots (residuals vs. fitted, Q-Q plot)
- Hours: 22 hours
- Key deliverable: `capstone_models.py` (Model A and Model B implementations, diagnostics sections)

### Milestone 4: Final Investment Memo (Week 14)
- Formatted and verified all regression tables from M3 outputs for inclusion in memo
- Created the robustness coefficient comparison table showing stability across specifications
- Compiled forecast accuracy table (ARIMA vs. naive, OLS vs. RF)
- Hours: 8 hours
- Key deliverable: Tables 1 and 2 in Final_Investment_Memo.md; verified all exported CSV sources

**Total Hours:** 70 hours

---

## 2. One Defended Methodological Decision

**Decision:** Lagged all disaster variables by 1 year (log_total_damage_l1, event_count_l1) rather than using contemporaneous values

**Reasoning:** 
- Evidence: M2 lag analysis showed that housing growth is most sensitive to mortgage rates at lag 0 (r = -0.479) but weakens as lag increases (lag 1: -0.388, lag 2: -0.268). This informed a lag structure search for disaster variables.
- Economic justification: Disaster damage and repairs take months to register in local housing markets. Immediate post-disaster, properties are often in active repair; valuation adjustments are gradual. Contemporaneous disaster damage would artificially inflate the estimated effect size.
- Robustness support: M3 tested lags 1, 2, 3. All three showed coefficients near zero and insignificant (lag 1 p=0.715, lag 2 p=0.985, lag 3 p=0.976), confirming that the lag choice does not drive the conclusion.

**Alternative considered:** Using contemporaneous disaster values (lag 0) for simplicity
- Why not: This would conflate in-construction recovery activity with actual price signals and would likely overstate disaster effects. The theory and M2 evidence support a transmission lag.

---

## 3. One Key Limitation of Our Analysis

**Limitation:** The outcome variable (yoy_real) is a national home price index replicated across all 3,347 counties in the panel. With year fixed effects, all national-level variation is absorbed, leaving only cross-county residual variation for identification.

**Why this matters:** This design structure severely limits the power to detect disaster effects. County fixed effects capture time-invariant differences (geography, baseline risk), but the outcome itself does not vary across counties in any given year—it only varies across years. The true identification would require county-level housing price indices, which are not available for the full 1980–2022 period. As a result, the "no effect" finding may reflect a data-design limitation rather than a true causal null.

**Potential mitigation:** Use Case-Shiller zip-code level indices (available post-1987) or compile repeat-sales indices from FHFA county-level data to create truly local outcomes. Alternatively, use a placebo test by assigning disasters to non-treated years and confirming that pre-existing trends do not predict the false "treatment."

---

## 4. AI Audit — Detailed Examples

### Example 1: NOAA Storm Events Download and Parsing
- **Prompt:** "How do I auto-download NOAA Storm Events CSV files from the public S3 directory, parse state and county FIPS, and convert damage strings like '10K', '1.5M', '500B' to float USD?"
- **Output:** Initial script with regex damage parsing and directory listing via boto3
- **Verification:** Downloaded 1960–2024 NOAA files; confirmed 1,237,984 raw rows saved; spot-checked damage values (1960 range ~$1K–$100M per event, consistent with historical disaster scales); verified 3,347 unique county FIPSes
- **Critique:** Initial script used incorrect regex for 'M' suffix (treated as millions but should handle both numeric and alpha). I debugged by manually inspecting a few rows and revising the regex to handle '2.5M' → 2.5e6, '1B' → 1e9 correctly.

### Example 2: Shiller Parser Column Fix
- **Prompt:** "The Shiller Fig3-1.xls file has CPI and real HPI columns, but my code returns all NaNs. How do I inspect the XLS structure?"
- **Output:** Code to read all sheet names and column headers; revealed 19 columns with interleaved series
- **Verification:** Manually inspected raw XLS in Python; confirmed column 14 = BLS CPI (values ~29 in 1960, ~300 in 2022). Recomputed real_hpi(2000) ≈ nominal_hpi(2000) per the 2000-base normalization, confirming the fix.
- **Critique:** Initial code assumed a simple 4-column layout; Shiller's layout is idiosyncratic. I verified the fix by spot-checking 5 years of data against published Shiller real HPI to confirm accuracy.

### Example 3: PanelOLS Fixed Effects Implementation
- **Prompt:** "How do I fit a two-way FE model with linearmodels.PanelOLS and get both standard and clustered standard errors?"
- **Output:** Code using PanelOLS with entity_effects=True, time_effects=True, cov_type="clustered", cluster_entity=True
- **Verification:** Ran the model on our data; confirmed N=112,790 and output shape. Cross-checked coefficients against a manual FE demean check: coefficients matched to machine precision.
- **Critique:** Initial code did not set drop_absorbed=True, which caused a sparse matrix warning. I added that parameter to clean up output.

### Overall AI Use
**Estimate:** Approximately 40% of my work involved AI assistance (primarily data pipeline scaffolding, debugging, and syntax). All econometric specifications, model choice, and robustness check design were my own; I used AI for implementation details, not conceptual inference.

**Types of help:** Database queries, regex patterns, pandas/statsmodels syntax, error diagnosis
**What I verified independently:** All AI-generated code was run on our actual dataset; I spot-checked outputs (row counts, value ranges, coefficient magnitudes) against expected results before accepting the code.

---

## 5. Self-Reflection

### What did I do particularly well on this capstone?
I excelled at architecting and debugging the data pipeline. Getting four separate data sources to merge cleanly without duplicates or dropped rows required careful logic design and verification. I'm proud that the final pipeline is reproducible—anyone can run `fetch_*.py` scripts in sequence and reliably produce the same 116K-row panel.

### What could I have improved?
I could have started M3 econometric work earlier. I waited until the week before the deadline, which limited my ability to explore alternative model specifications (e.g., dynamic panel estimators or sector-heterogeneous effects). More time would have enabled deeper robustness checks.

### What did I learn from this capstone project?
I learned that data engineering is the foundation of any analysis. Cleaning, validating, and documenting the data pipeline consumed 40% of my effort but eliminated weeks of downstream debugging. I also learned the value of paired specification testing: by running FE models across lags, SEs, and crisis periods, we built confidence that our null result was robust rather than an artifact of one choice. Most importantly, I developed confidence working with real, messy federal data and building reproducible workflows from raw downloads to analysis-ready panels.

---

## 6. Attestation

By submitting this individual addendum, I affirm that:
- ☑ All contributions listed above are accurate and honest
- ☑ I have not exaggerated my role or minimized teammates' contributions
- ☑ I understand this addendum may be used to adjust my individual grade relative to the team grade
- ☑ I take full responsibility for my work and any errors in the sections I authored

**Signature:** _________________________________ **Date:** May 1, 2026
