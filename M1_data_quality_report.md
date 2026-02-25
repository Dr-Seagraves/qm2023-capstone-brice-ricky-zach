# M1 Data Quality Report

**Project:** How do repeated natural disasters affect local housing price growth and volatility in high-risk counties?  
**Team:** Brice, Ricky, Zach  
**Course:** QM 2023: Statistics II / Data Analytics  
**Date:** February 25, 2026

---

## 1. Data Sources

### Primary Dataset: NOAA Storm Events
- **Source:** NOAA National Centers for Environmental Information (NCEI)
- **URL:** https://www.ncei.noaa.gov/pub/data/swdi/stormevents/csvfiles/
- **Access:** Fully public — no account or API key required; auto-downloaded via `fetch_sheldus_data.py`
- **Coverage:** U.S. county-level natural disaster events, 1960–2024
- **Variables captured:** event type, state, county FIPS, property damage, crop damage, injuries, fatalities
- **Note:** Originally planned to use SHELDUS (ASU CEMHS), but their online query tool caps exports. NOAA Storm Events is the authoritative federal source underlying SHELDUS and provides identical variables with no access restrictions.

### Supplementary Dataset 1: Shiller Home Price Index
- **Source:** Robert J. Shiller, Yale University
- **URL:** http://www.econ.yale.edu/~shiller/data/Fig3-1.xls
- **Access:** Publicly available XLS; auto-downloaded via `fetch_shiller_data.py`
- **Coverage:** U.S. national home price index, monthly, 1890–2023
- **Variables captured:** nominal HPI, CPI (BLS), real HPI, year-over-year changes

### Supplementary Dataset 2: FRED Macro Controls
- **Source:** Federal Reserve Bank of St. Louis (FRED REST API)
- **URL:** https://fred.stlouisfed.org/
- **Access:** Free API key required; auto-downloaded via `fetch_fred_data.py`
- **Coverage:** Monthly/weekly series, 1960–present
- **Series downloaded:**

| FRED ID | Variable | Frequency |
|---|---|---|
| MORTGAGE30US | 30-year fixed mortgage rate | Weekly |
| UNRATE | U.S. unemployment rate | Monthly |
| CPIAUCSL | CPI all items | Monthly |
| FEDFUNDS | Federal Funds rate | Monthly |
| GS10 | 10-year Treasury yield | Monthly |
| CSUSHPISA | Case-Shiller national HPI (SA) | Monthly |

---

## 2. Cleaning Decisions

### 2a. NOAA Storm Events

| Decision | Before | After | Justification |
|---|---|---|---|
| Filter to county-level records only (`CZ_TYPE == 'C'`) | ~1.8M event rows | 1,237,984 rows | Zone-type records lack county FIPS; cannot be merged to county panel |
| Drop rows missing state or county FIPS | 1,237,984 | 1,237,984 | No rows dropped — all county records have valid FIPS |
| Convert damage strings (e.g. "10K", "2.5M") to numeric USD | string | float | NOAA encodes damage with multiplier suffixes; requires parsing |
| Sum direct + indirect injuries and fatalities | two cols each | one col each | Both direct and indirect casualties are economically relevant |
| Aggregate event-level to county-year | 1,237,984 events | 150,227 county-year rows | Unit of analysis is county-year; event count captures frequency |
| Filter to years 1960–2024 | 1950–2024 | 1960–2024 | Pre-1960 NOAA data is sparse and unreliable for many hazard types |

**Derived variables:**
- `total_damage` = `property_damage` + `crop_damage`
- `event_count` = count of events per county-year

### 2b. Shiller Home Price Index

| Decision | Before | After | Justification |
|---|---|---|---|
| Parse XLS header at row 7 | multi-section spreadsheet | structured DataFrame | Shiller's workbook has metadata rows above the data table |
| Extract nominal HPI from col 1, CPI from col 14 | 19 interleaved columns | 3 clean columns | Shiller's XLS has multiple series interleaved; cols 2–6 are only available through 1953 |
| Average 12 monthly observations per year | 904 monthly rows | 64 annual rows | All other datasets are annual; monthly variation averaged out |
| Compute `real_hpi` = nominal_hpi / cpi × cpi_base_2000 | nominal only | nominal + real | Inflation-adjustment required to isolate real housing value changes |
| Filter to 1960–2024 | 1890–2023 | 1960–2023 | Pre-1960 observations not needed for project scope |

### 2c. FRED Macro Controls

| Decision | Before | After | Justification |
|---|---|---|---|
| Drop non-numeric FRED values (`.` placeholders) | mixed | numeric only | FRED uses `.` for missing observations; coerced to NaN then dropped |
| Average weekly/monthly observations to annual | 3,571 obs (mixed frequency) | 67 annual rows | Aligns with county-year panel structure |
| Compute year-over-year changes for HPI and CPI | levels | levels + YoY % | Rate of change captures momentum; levels capture absolute environment |

---

## 3. Merge Strategy and Verification

### Strategy
- **Base:** NOAA Storm Events county-year panel (150,227 rows)
- **Join 1:** Left join Shiller on `year` → adds national HPI, CPI, real HPI, YoY changes
- **Join 2:** Left join FRED on `year` → adds mortgage rates, unemployment, fed funds, Treasury yield, Case-Shiller
- **Year filter:** Restrict to 1980–2022 (NOAA coverage improves post-1980; avoids incomplete 2023–2024 data)

### Verification

| Check | Result |
|---|---|
| Row count before merge | 150,227 |
| Row count after both joins | 150,227 (no duplication) |
| Row count after year filter | 116,137 |
| Unique counties in final panel | 3,347 |
| Year range in final panel | 1980–2022 |
| Columns in final panel | 24 |
| Duplicate (fips, year) pairs | 0 |
| Missing FIPS values | 0 |
| Missing year values | 0 |

### Missing Values in Final Panel

| Variable | Missing % | Reason |
|---|---|---|
| `case_shiller_national` | 12.1% | Case-Shiller series begins 1987; years 1980–1986 are NaN |
| `case_shiller_national_yoy` | 13.9% | One additional year lost to first-difference calculation |
| All other variables | 0% | Fully populated |

---

## 4. Final Dataset Summary

**File:** `data/final/housing_disasters_panel.csv`  
**Dimensions:** 116,137 rows × 24 columns  
**Unit of analysis:** County × Year  
**Unique counties:** 3,347  
**Year range:** 1980–2022  

### Sample Statistics

| Variable | Count | Mean | Std | Min | Max |
|---|---|---|---|---|---|
| `event_count` | 116,137 | 9.40 | 10.51 | 1 | 232 |
| `total_damage` (USD) | 116,137 | 2,161,923 | 61,770,567 | 0 | 10,002,030,000 |
| `total_injuries` | 116,137 | 0.62 | 8.56 | 0 | 1,151 |
| `total_fatalities` | 116,137 | 0.07 | 0.77 | 0 | 162 |
| `nominal_hpi` | 116,137 | 144.61 | 29.38 | 108.41 | 218.25 |
| `real_hpi` | 116,137 | 140.67 | 30.39 | 98.54 | 244.74 |
| `yoy_nominal` (%) | 116,137 | 1.70 | 5.26 | -12.21 | 11.75 |
| `mortgage_rate_30yr` (%) | 116,137 | 7.05 | 3.20 | 2.96 | 16.64 |
| `unemployment_rate` (%) | 116,137 | 6.06 | 1.68 | 3.65 | 9.71 |
| `log_total_damage` | 116,137 | 6.65 | 5.87 | 0 | 23.03 |

---

## 5. Reproducibility Checklist

- [x] All data is fetched automatically via scripts — no manual downloads required
- [x] All file paths use `config_paths.py` with `Path(__file__).resolve()` — no hardcoded absolute paths
- [x] Scripts run in sequence without errors using `.venv` Python environment
- [x] Raw data saved to `data/raw/` before any transformation
- [x] Processed data saved to `data/processed/` after cleaning
- [x] Final merged panel saved to `data/final/`
- [x] Before/after row counts printed at each cleaning step
- [x] Summary statistics printed at completion of each script
- [x] FRED API key stored in script constant (not hardcoded in pipeline logic); can be overridden via `FRED_API_KEY` environment variable
- [x] `requirements.txt` documents all dependencies

**To reproduce from scratch:**
```bash
source .venv/bin/activate
python code/fetch_sheldus_data.py   # ~5 min
python code/fetch_shiller_data.py   # ~10 sec
python code/fetch_fred_data.py      # ~30 sec
python code/merge_final_panel.py    # ~10 sec
```

---

## 6. Ethical Considerations

### What data are we losing?

| Loss | Description | Economic Impact |
|---|---|---|
| **Pre-1980 county observations** | NOAA Storm Events records before 1980 are sparse and inconsistently coded across hazard types | We may underestimate cumulative disaster exposure for counties with long disaster histories |
| **Zone-type NOAA records** | NOAA assigns some events to forecast zones rather than counties; these are excluded | Undercounts events in areas where NOAA uses zone-based reporting (e.g., coastal, marine zones) |
| **Counties with zero events** | Only counties with at least one recorded disaster appear in the NOAA data; zero-event counties are absent from the panel | Creates selection bias — our panel over-represents disaster-prone counties; we cannot compare against truly disaster-free counties |
| **National vs. county HPI** | Shiller and FRED provide only national home price indices; we have no county-level HPI | We can measure whether disasters deviate from national trends but cannot directly measure absolute county-level home price changes |
| **Damage underreporting** | NOAA property damage estimates are based on initial reports and may understate true economic losses, especially for older events | Right-censors damage distribution; particularly affects pre-1990 records |
| **Small/rural counties** | Counties with few events may be missing years entirely from the panel | Panel is unbalanced; rural low-disaster counties may be underrepresented |

### Potential Biases
- **Survivorship bias:** Counties that experienced catastrophic damage and were subsequently depopulated or reorganized (e.g., post-Katrina parishes) may have unusual or missing records.
- **Reporting improvements over time:** NOAA Storm Events documentation has improved substantially since 1996 when reporting was standardized. Pre-1996 data systematically undercounts events, which may create artificial time trends in our disaster variables.
