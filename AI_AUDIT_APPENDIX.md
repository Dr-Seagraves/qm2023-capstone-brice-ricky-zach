# AI Audit Appendix — M1 Data Pipeline

**Project:** How do repeated natural disasters affect local housing price growth and volatility in high-risk counties?  
**Team:** Brice, Ricky, Zach  
**Course:** QM 2023: Statistics II / Data Analytics  
**Due:** February 25, 2026  
**Framework:** Disclose → Verify → Critique

---

## Overview of AI Tool Use

| Tool | Purpose | Tasks |
|---|---|---|
| GitHub Copilot (Claude Sonnet 4.6) | Code generation, debugging, data pipeline development | All items below |

All AI interactions occurred within VS Code using the GitHub Copilot Chat interface during the M1 milestone development session on February 25, 2026.

---

## Disclose — What AI Was Asked to Do

### 1. Data Source Substitution
**Prompt context:** SHELDUS (ASU CEMHS) was the originally planned data source for county-level disaster data. The online query tool returned an error stating exports exceeded maximum allowed records even when filtered to 5-year windows.

**AI contribution:** Identified NOAA Storm Events (NCEI) as a drop-in substitute with identical variables (property damage, crop damage, injuries, fatalities, county FIPS) and no download limits. Provided the public S3 URL structure and confirmed file naming conventions by querying the NOAA directory listing.

---

### 2. `fetch_sheldus_data.py` — Full Rewrite
**Original script:** Loaded a manually downloaded SHELDUS CSV file that did not exist.

**AI contribution:** Completely rewrote the script to:
- Auto-discover available year files from the NOAA directory listing via regex
- Download and decompress 65 individual `.csv.gz` files (1960–2024)
- Parse NOAA-specific damage encoding (`10K`, `2.5M`, `1B` → float USD)
- Build 5-digit FIPS from state + county FIPS columns
- Filter to county-type records only (`CZ_TYPE == 'C'`)
- Aggregate 1.2M event rows to 150,227 county-year records
- Save both raw and processed outputs

---

### 3. `fetch_shiller_data.py` — Parser Fix
**Problem:** `cpi`, `real_hpi`, and `yoy_real` columns were 100% missing in the output.

**AI contribution:** Diagnosed the issue by inspecting the raw XLS structure. Found that Shiller's `Fig3-1.xls` has 19 interleaved columns across multiple series; the original parser assumed CPI was in column 2 but it is actually in column 14 (BLS series). Fixed the parser to read the correct column, compute `real_hpi` by deflating nominal HPI by CPI (re-based to year 2000), and populate all derived columns.

---

### 4. `fetch_fred_data.py` — Diagnosis
**Problem:** Script exited with code 1 when run via the VS Code Run button.

**AI contribution:** Diagnosed that the failure was caused by VS Code using `/usr/bin/python3` (system Python without project dependencies) instead of `.venv/bin/python`. Confirmed the script ran successfully with exit code 0 when executed with the venv activated. Updated `.vscode/settings.json` to enforce `.venv/bin/python` as the default interpreter.

---

### 5. `merge_final_panel.py` — Verification
**AI contribution:** Ran the merge script, interpreted output, and identified that `cpi`, `real_hpi`, and `yoy_real` were 100% missing (traced to the Shiller parser bug fixed above). Confirmed post-fix that the only remaining missing values (`case_shiller_national` at 12.1%, `case_shiller_national_yoy` at 13.9%) are expected and explained by the Case-Shiller series starting in 1987.

---

### 6. Documentation Files
**AI contribution:** Created or substantially updated the following files:
- `README.md` — Added pipeline status table, updated datasets table with NOAA sources, key variables table with actual column names, and corrected run instructions
- `data/final/data_dictionary.md` — Fixed 4 variables with "Unknown" source/description; updated all SHELDUS source labels to NOAA Storm Events
- `M1_data_quality_report.md` — Created from scratch with all 6 required sections (data sources, cleaning decisions with before/after counts, merge verification, summary statistics, reproducibility checklist, ethical considerations)

---

## Verify — How AI Output Was Checked

| AI Output | Verification Method | Result |
|---|---|---|
| NOAA as SHELDUS substitute | Checked that NOAA Storm Events contains the same county FIPS, damage, injury, and fatality fields documented in SHELDUS literature | Confirmed — columns match |
| `fetch_sheldus_data.py` rewrite | Ran script; confirmed 1,237,984 raw rows saved to `data/raw/sheldus_raw.csv` and 150,227 county-year rows to `data/processed/sheldus_clean.csv` | ✓ Verified |
| Shiller parser fix (col 14 = CPI) | Inspected raw XLS in Python to confirm column 14 contained BLS CPI values for 1960+ rows | ✓ Verified — values matched expected CPI range (~29 in 1960, ~293 in 2022) |
| `real_hpi` computation | Spot-checked: real_hpi(2000) ≈ nominal_hpi(2000), consistent with 2000-base normalization | ✓ Verified |
| Final panel dimensions | Confirmed 116,137 rows × 24 columns, 3,347 unique counties, 0 duplicate (fips, year) pairs | ✓ Verified |
| Missing value explanation | Confirmed Case-Shiller series (CSUSHPISA) starts January 1987 on FRED; 1980–1986 panel rows correctly show NaN | ✓ Verified |

---

## Critique — Limitations of AI-Generated Work

### What AI got right
- Correctly identified the NOAA directory structure and file naming convention without hallucination — output was verified against the live directory.
- The Shiller column-position diagnosis was accurate and confirmed by directly inspecting the XLS.
- All scripts produced correct output that matched expected dimensions and value ranges.

### What required human judgment or could be wrong
- **NOAA vs. SHELDUS equivalence:** While NOAA Storm Events is the federal source underlying SHELDUS, the two databases may differ in pre-1996 event coverage and damage estimation methodology. We did not perform a formal cross-validation — this should be noted as a limitation in M2.
- **Real HPI computation:** The choice to re-base to year-2000 CPI is one methodological option; other baselines (1890, 2010) are also common in the housing literature. Our choice was not validated against published Shiller real HPI values.
- **Data dictionary descriptions:** AI-generated variable descriptions were reviewed for accuracy but some nuances (e.g., exactly which BLS CPI series Shiller uses) were not independently verified against Shiller's technical appendix.
- **Ethical considerations section:** The data loss items identified (zone-type records, pre-1996 underreporting, zero-event counties) are plausible and well-reasoned but represent AI-generated analysis, not a systematic audit. A formal assessment of county coverage relative to Census FIPS would strengthen this section.
- **Zero-event county gap:** The panel only contains counties with at least one recorded event. The AI correctly flagged this as a selection bias issue, but the merge script does not attempt to fill in zero-event county-years from a Census county list. This should be addressed in M2 if cross-sectional comparison to quiet counties is needed.

---

# AI Audit Appendix — M2 EDA Dashboard Addendum

**Milestone:** M2 Exploratory Data Analysis Dashboard  
**Date:** March 27, 2026  
**Tooling:** GitHub Copilot Chat (GPT-5.3-Codex) in VS Code

## Disclose — What AI Was Asked to Do

### 1. Build complete M2 EDA deliverables
**Prompt context:** Team requested implementation of all M2 requirements including notebook visuals, summary report, and required output files.

**AI contribution:**
- Created `results/reports/capstone_eda.ipynb` with 8 publication-style plots and captions.
- Saved all figures to `results/figures/` as `M2_plot*.png`.
- Created `results/reports/M2_EDA_summary.md` with key findings, M3 hypotheses, and data-quality mitigation plan.

### 2. Implement conditional group sensitivity analysis
**Prompt context:** Assignment requires Plot 6 when natural groups exist and alternatives otherwise.

**AI contribution:**
- Constructed region groups from county state FIPS.
- Computed `group_sensitivity = corr(yoy_real, mortgage_rate_30yr)` by region.
- Produced horizontal bar chart with sensitivity threshold coloring (`r < -0.3` flagged as sensitive).
- Listed sensitive groups to motivate group x driver interaction terms in M3.

### 3. Add required factor/control scatter plots and decomposition
**Prompt context:** Plot 7 and Plot 8 are required.

**AI contribution:**
- Implemented `sns.regplot()` scatter + regression line panels for `yoy_real` vs `unemployment_rate` and `treasury_10yr`.
- Implemented time-series decomposition of annual mean `yoy_real` using `seasonal_decompose` and saved a 4-panel output (observed/trend/cyclical/residual).

### 4. Address prior milestone feedback (config paths)
**Prompt context:** Instructor noted `config_paths.py` bug from M1.

**AI contribution:**
- Refactored root-detection logic in `code/config_paths.py` to rely on project-structure checks.
- Removed import-time print side effects to avoid noisy/non-deterministic behavior during script imports.

## Verify — How AI Output Was Checked

| AI Output | Verification Method | Result |
|---|---|---|
| Notebook execution | Ran `jupyter nbconvert --to notebook --execute --inplace results/reports/capstone_eda.ipynb` | Passed with no execution errors |
| Figure generation | Checked `results/figures/` for all M2 outputs | 8/8 required plot PNGs present |
| Numeric findings | Recomputed key correlations and lag statistics in a separate Python check | Values consistent with notebook interpretations |
| Group sensitivity flags | Verified regional correlations against threshold rule `r < -0.3` | Sensitive groups correctly identified |

## Critique — Limitations of AI-Generated Work

- **Group-definition approximation:** Regional grouping uses state-FIPS-to-Census-region mapping, which is valid but coarse. Finer subgrouping (coastal vs inland, hazard-specific exposure) may reveal additional heterogeneity.
- **Decomposition on annual data:** Seasonal decomposition is used to satisfy assignment structure, but annual frequency does not support literal within-year seasonality. The periodic component should be interpreted as medium-run cyclicality.
- **Panel structure constraints:** National macro controls vary by year, not county, so cross-sectional identification for macro factors relies on county fixed effects and interaction structure in M3.
- **Potential omitted county-year zeros:** Without an explicit full county-year backbone, event-derived sampling may still underweight quiet counties; this should be addressed in M3 robustness checks.
