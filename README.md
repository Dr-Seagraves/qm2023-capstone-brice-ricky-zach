[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/gp9US0IQ)
[![Open in Visual Studio Code](https://classroom.github.com/assets/open-in-vscode-2e0aaae1b6195c2367325f4f02e2d04e9abb55f0b24a779b69b11b9e10269abc.svg)](https://classroom.github.com/online_ide?assignment_repo_id=22634811&assignment_repo_type=AssignmentRepo)
# QM 2023 Capstone Project

**Course:** QM 2023: Statistics II / Data Analytics  
**Semester:** Spring 2026

## Team Members

| Name | Role |
|---|---|
| Brice | Created the branch, posted research question to discussion board |
| Ricky | Verified Zach's work and completed the M1 assignment documentation |
| Zach | Fetched and verified all datasets; built the data pipeline |

---

## Research Question

> **How do repeated natural disasters affect local housing price growth and volatility in high-risk counties?**

Climate-related disasters are becoming more frequent and costly. This project tests whether repeated disaster exposure creates persistent housing market discounts — and whether certain county characteristics amplify or dampen that effect.

### Preliminary Hypotheses

1. Counties with higher cumulative disaster losses will show slower home price growth over 5–10 year windows.
2. Disaster frequency (event count) will increase housing price volatility even when average losses are moderate.
3. The negative effect of disasters on home prices will be stronger in counties with higher mortgage exposure and lower median incomes.

---

## Datasets

| Dataset | Source | What It Provides | Geographic Level |
|---|---|---|---|
| NOAA Storm Events | [NOAA NCEI](https://www.ncei.noaa.gov/pub/data/swdi/stormevents/csvfiles/) — auto-downloaded | County-level disaster events, property/crop damage, injuries, fatalities (1960–2024) | County (FIPS) |
| Shiller Home Price Index | [Yale/Shiller](http://www.econ.yale.edu/~shiller/data/Fig3-1.xls) — auto-downloaded | U.S. national nominal & real home price index, CPI (1960–2023) | National |
| FRED Macro Controls | [FRED REST API](https://fred.stlouisfed.org/) — auto-downloaded | Mortgage rates, unemployment, CPI, fed funds rate, 10-yr Treasury, Case-Shiller national HPI (1960–present) | National |

> **Note on disaster data:** The original plan used SHELDUS (ASU CEMHS), but their export tool caps downloads. NOAA Storm Events is the underlying federal source for SHELDUS and provides identical variables with no download limits.

---

## Key Variables

| Role | Variable | Source |
|---|---|---|
| **Outcome** | `nominal_hpi`, `real_hpi`, `yoy_nominal`, `yoy_real` | Shiller |
| **Driver** | `event_count`, `total_damage`, `total_injuries`, `total_fatalities` | NOAA Storm Events |
| **Controls** | `mortgage_rate_30yr`, `unemployment_rate`, `fed_funds_rate`, `treasury_10yr` | FRED |
| **Supplemental** | `case_shiller_national`, `cpi_all_items` | FRED |
| **ID** | `fips` (5-digit county FIPS), `year` | — |

---

## Data Pipeline Status (M1)

| Step | Script | Output | Status |
|---|---|---|---|
| Fetch disaster data | `fetch_sheldus_data.py` | `data/raw/sheldus_raw.csv` (1.2M rows) | ✓ Complete |
| Clean disaster data | `fetch_sheldus_data.py` | `data/processed/sheldus_clean.csv` (150K county-years) | ✓ Complete |
| Fetch home price data | `fetch_shiller_data.py` | `data/raw/shiller_raw.xls` | ✓ Complete |
| Clean home price data | `fetch_shiller_data.py` | `data/processed/shiller_clean.csv` (64 years) | ✓ Complete |
| Fetch macro controls | `fetch_fred_data.py` | `data/raw/fred_raw.csv` (3,571 obs) | ✓ Complete |
| Clean macro controls | `fetch_fred_data.py` | `data/processed/fred_clean.csv` (67 years) | ✓ Complete |
| Merge final panel | `merge_final_panel.py` | `data/final/housing_disasters_panel.csv` (116K rows) | ✓ Complete |

**Final panel:** 116,137 rows × 24 columns | 3,347 counties | Years 1980–2022

---

## Repository Structure

```
qm2023-capstone-brice-ricky-zach/
├── code/
│   ├── config_paths.py              # Path management — use for all file I/O
│   ├── fetch_sheldus_data.py        # Auto-downloads NOAA Storm Events (1960–2024)
│   ├── fetch_shiller_data.py        # Auto-downloads Shiller HPI (1960–2023)
│   ├── fetch_fred_data.py           # Auto-downloads FRED macro controls (API key required)
│   └── merge_final_panel.py         # Merges processed datasets → final panel
├── data/
│   ├── OpenData_rows.csv            # Dataset catalog reference
│   ├── raw/                         # Original downloaded data (read-only)
│   │   ├── sheldus_raw.csv          # NOAA Storm Events combined raw (1.2M rows)
│   │   ├── shiller_raw.xls          # Shiller Fig3-1.xls
│   │   └── fred_raw.csv             # FRED monthly observations
│   ├── processed/                   # Cleaned individual datasets
│   │   ├── sheldus_clean.csv        # County-year disaster panel (150K rows)
│   │   ├── shiller_clean.csv        # Annual national HPI (64 rows)
│   │   └── fred_clean.csv           # Annual macro controls (67 rows)
│   └── final/                       # Analysis-ready merged panel
│       ├── housing_disasters_panel.csv   # Final dataset (116K rows × 24 cols)
│       └── data_dictionary.md            # Variable definitions
├── results/
│   ├── figures/                     # Visualizations
│   ├── tables/                      # Regression tables, summary stats
│   └── reports/                     # Milestone memos
├── tests/                           # Autograding test suite
├── README.md                        # This file
├── M1_data_quality_report.md        # M1: Data cleaning documentation
├── AI_AUDIT_APPENDIX.md             # M1: Required AI disclosure
└── M1-assignment-description.md     # Assignment prompt reference
```

---

## How to Run the Pipeline

```bash
# 1. Activate the virtual environment
source .venv/bin/activate

# 2. Fetch and clean each dataset (all auto-download — no manual steps needed)
python code/fetch_sheldus_data.py   # ~5 min — downloads 65 years of NOAA data
python code/fetch_shiller_data.py   # ~10 sec
python code/fetch_fred_data.py      # ~30 sec — requires FRED API key (see script)

# 3. Merge into final panel
python code/merge_final_panel.py
```

**FRED API key:** Get a free key at https://fred.stlouisfed.org/docs/api/api_key.html and set it in `code/fetch_fred_data.py` (`FRED_API_KEY_FALLBACK`) or via `export FRED_API_KEY="your_key"`.

Final output: `data/final/housing_disasters_panel.csv`
