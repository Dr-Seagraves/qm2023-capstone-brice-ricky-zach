# Data Dictionary — Housing Disasters Panel

**Dataset:** `housing_disasters_panel.csv`  
**Entities (counties):** 3,347  
**Time periods (years):** 43 (1980–2022)  
**Total observations:** 116,137  
**Unit of analysis:** County × Year (long format)

---

## Variable Definitions

| Variable | Type | Source | Description | Units |
|---|---|---|---|---|
| `fips` | string | NOAA Storm Events | 5-digit county FIPS code (zero-padded) | — |
| `year` | int | NOAA Storm Events | Calendar year | — |
| `event_count` | int | NOAA Storm Events | Number of natural disaster events in county-year | count |
| `total_damage` | float | NOAA Storm Events | Total property + crop damage from all disaster events | USD |
| `property_damage` | float | NOAA Storm Events | Total property damage from all disaster events in county-year | USD |
| `crop_damage` | float | NOAA Storm Events | Total crop damage from all disaster events in county-year | USD |
| `total_injuries` | float | NOAA Storm Events | Total injuries from all disaster events | count |
| `total_fatalities` | float | NOAA Storm Events | Total fatalities from all disaster events | count |
| `nominal_hpi` | float | Shiller | U.S. national nominal home price index (1890 base = 100) | index |
| `cpi` | float | Shiller | Consumer Price Index used by Shiller for real HPI deflation (BLS series) | index |
| `real_hpi` | float | Shiller | CPI-deflated real home price index | index |
| `yoy_nominal` | float | Shiller | Year-over-year % change in nominal HPI | % |
| `yoy_real` | float | Shiller | Year-over-year % change in real HPI | % |
| `mortgage_rate_30yr` | float | FRED | 30-year fixed mortgage rate (MORTGAGE30US) | % p.a. |
| `unemployment_rate` | float | FRED | U.S. national unemployment rate (UNRATE) | % |
| `cpi_all_items` | float | FRED | CPI for all urban consumers (CPIAUCSL) | index |
| `fed_funds_rate` | float | FRED | Federal Funds effective rate (FEDFUNDS) | % p.a. |
| `treasury_10yr` | float | FRED | 10-year Treasury yield (GS10) | % p.a. |
| `case_shiller_national` | float | FRED | Case-Shiller U.S. national HPI, SA (CSUSHPISA) | index |
| `case_shiller_national_yoy` | float | FRED | YoY % change in Case-Shiller national HPI | % |
| `cpi_all_items_yoy` | float | FRED | Year-over-year % change in CPI all items (CPIAUCSL) | % |
| `mortgage_rate_chg` | float | FRED | Annual change in 30yr mortgage rate | pp |
| `log_total_damage` | float | Derived | Natural log of (total_damage + 1); controls right-skew | log USD |
| `disaster_intensity` | cat | Derived | Binned event count: none/low/moderate/high/very_high | — |

---

## Cleaning Decisions

| Decision | Justification |
|---|---|
| Aggregated NOAA Storm Events event-level records to county-year | Unit of analysis is county-year; event multiplicity captured in `event_count` |
| Filtered to 1980–2022 | NOAA Storm Events coverage improves post-1980; Shiller/FRED series available throughout |
| Log-transformed `total_damage` | Property damage is heavily right-skewed; log(damage+1) reduces influence of extreme events |
| Left-joined Shiller + FRED on year | National macro series apply uniformly to all counties in a given year |
| Dropped rows with missing FIPS or year | Cannot assign to panel without both keys |
| Padded FIPS to 5 digits | Ensures consistent join keys across datasets |

---

## Sources

- **NOAA Storm Events**: NOAA National Centers for Environmental Information (NCEI). https://www.ncei.noaa.gov/pub/data/swdi/stormevents/csvfiles/
- **Shiller Data**: Robert J. Shiller, Yale University. https://shillerdata.com/
- **FRED**: Federal Reserve Bank of St. Louis. https://fred.stlouisfed.org/