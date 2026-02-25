"""
merge_final_panel.py
====================
Merges all processed datasets into the analysis-ready panel.

Input files (data/processed/):
  sheldus_clean.csv    – county-year disaster events and losses
  shiller_clean.csv    – annual U.S. national home price index (HPI)
  fred_clean.csv       – annual macro controls (mortgage rate, unemployment, CPI, etc.)

Merge strategy:
  Base:  SHELDUS  (county × year)  ← the unit of analysis
  Join:  Shiller  on year          ← national HPI as reference index
  Join:  FRED     on year          ← macro controls

Output:
  data/final/housing_disasters_panel.csv
  data/final/data_dictionary.md

Panel structure:
  One row per (fips, year)
  Long format — ready for panel regression in M2/M3
"""

import sys
import pandas as pd
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from config_paths import PROCESSED_DATA_DIR, FINAL_DATA_DIR

# -----------------------------------------------------------------------------
# File paths
# -----------------------------------------------------------------------------
SHELDUS_FILE = PROCESSED_DATA_DIR / 'sheldus_clean.csv'
SHILLER_FILE = PROCESSED_DATA_DIR / 'shiller_clean.csv'
FRED_FILE    = PROCESSED_DATA_DIR / 'fred_clean.csv'
OUT_PANEL    = FINAL_DATA_DIR / 'housing_disasters_panel.csv'
OUT_DICT     = FINAL_DATA_DIR / 'data_dictionary.md'

# Year range for the final panel
YEAR_MIN = 1980
YEAR_MAX = 2022


# -----------------------------------------------------------------------------
# Loaders
# -----------------------------------------------------------------------------

def load(path: Path, label: str) -> pd.DataFrame:
    """Load a processed CSV and report shape."""
    if not path.exists():
        raise FileNotFoundError(
            f"[ERROR] {label} file not found: {path}\n"
            f"  → Run the corresponding fetch script first."
        )
    df = pd.read_csv(path, low_memory=False)
    print(f"  Loaded {label:<20} {df.shape[0]:>8,} rows × {df.shape[1]:>2} cols")
    return df


# -----------------------------------------------------------------------------
# Merge
# -----------------------------------------------------------------------------

def merge_panel(sheldus: pd.DataFrame,
                shiller: pd.DataFrame,
                fred: pd.DataFrame) -> pd.DataFrame:
    """
    Merge SHELDUS (county-year) with Shiller and FRED (year).

    Left join on year so every SHELDUS county-year gets macro context.
    Rows missing from Shiller or FRED get NaN (flagged below).
    """
    print("\n[Merge] SHELDUS ← Shiller (left join on year)...")
    df = sheldus.merge(shiller, on='year', how='left')
    print(f"  After Shiller merge: {df.shape}")

    print("[Merge] Panel ← FRED (left join on year)...")
    df = df.merge(fred, on='year', how='left')
    print(f"  After FRED merge:    {df.shape}")

    return df


# -----------------------------------------------------------------------------
# Clean merged panel
# -----------------------------------------------------------------------------

def clean_panel(df: pd.DataFrame) -> pd.DataFrame:
    """
    Post-merge cleaning:
      1. Filter to analysis window (YEAR_MIN – YEAR_MAX)
      2. Log-transform damage (heavy right-skew)
      3. Create disaster intensity bucket
      4. Verify no row duplication
      5. Sort by entity then time
    """
    before = len(df)

    # ── Year window ──────────────────────────────────────────────────────────
    df = df[(df['year'] >= YEAR_MIN) & (df['year'] <= YEAR_MAX)].copy()
    print(f"\n  Year filter ({YEAR_MIN}–{YEAR_MAX}): {before:,} → {len(df):,} rows")

    # ── Log damage ───────────────────────────────────────────────────────────
    if 'total_damage' in df.columns:
        df['log_total_damage'] = df['total_damage'].clip(lower=0).apply(
            lambda x: (x + 1).__class__.__mro__[0].__name__ and
                      pd.Series([x]).apply(lambda v: 0 if v <= 0 else __import__('math').log(v + 1)).iloc[0]
        )
        # Cleaner version:
        import math
        df['log_total_damage'] = df['total_damage'].clip(lower=0).apply(
            lambda x: math.log(x + 1)
        )

    # ── Disaster intensity bucket ────────────────────────────────────────────
    if 'event_count' in df.columns:
        df['disaster_intensity'] = pd.cut(
            df['event_count'],
            bins=[-1, 0, 2, 5, 10, float('inf')],
            labels=['none', 'low', 'moderate', 'high', 'very_high']
        )

    # ── Duplicate check ──────────────────────────────────────────────────────
    dup_count = df.duplicated(subset=['fips', 'year']).sum()
    if dup_count > 0:
        print(f"  WARNING: {dup_count:,} duplicate (fips, year) rows — keeping first occurrence")
        df = df.drop_duplicates(subset=['fips', 'year'], keep='first')

    # ── Sort ─────────────────────────────────────────────────────────────────
    df = df.sort_values(['fips', 'year']).reset_index(drop=True)

    return df


# -----------------------------------------------------------------------------
# Summary & verification
# -----------------------------------------------------------------------------

def verify(df: pd.DataFrame) -> None:
    """Print panel verification statistics."""
    print("\n" + "=" * 50)
    print("PANEL VERIFICATION")
    print("=" * 50)
    print(f"  Total rows:         {len(df):,}")
    print(f"  Unique counties:    {df['fips'].nunique():,}")
    print(f"  Year range:         {df['year'].min()} – {df['year'].max()}")
    print(f"  Columns:            {df.shape[1]}")

    # Missingness
    miss = df.isnull().mean() * 100
    miss_nonzero = miss[miss > 0].sort_values(ascending=False)
    if len(miss_nonzero) > 0:
        print("\n  Missing values (% per column):")
        for col, pct in miss_nonzero.items():
            print(f"    {col:<35} {pct:.1f}%")
    else:
        print("\n  ✓ No missing values")

    # Key variable stats
    print("\n  Key variable summary:")
    key_cols = [c for c in ['event_count', 'total_damage', 'nominal_hpi',
                             'mortgage_rate_30yr', 'unemployment_rate']
                if c in df.columns]
    if key_cols:
        print(df[key_cols].describe().round(2).to_string())


# -----------------------------------------------------------------------------
# Data dictionary
# -----------------------------------------------------------------------------

DATA_DICTIONARY = {
    'fips'                   : ('string', 'SHELDUS', '5-digit county FIPS code (zero-padded)', '—'),
    'year'                   : ('int',    'SHELDUS', 'Calendar year', '—'),
    'event_count'            : ('int',    'SHELDUS', 'Number of natural disaster events in county-year', 'count'),
    'total_damage'           : ('float',  'SHELDUS', 'Total property + crop damage from all disaster events', 'USD'),
    'total_injuries'         : ('float',  'SHELDUS', 'Total injuries from all disaster events', 'count'),
    'total_fatalities'       : ('float',  'SHELDUS', 'Total fatalities from all disaster events', 'count'),
    'log_total_damage'       : ('float',  'Derived', 'Natural log of (total_damage + 1); controls right-skew', 'log USD'),
    'disaster_intensity'     : ('cat',    'Derived', 'Binned event count: none/low/moderate/high/very_high', '—'),
    'nominal_hpi'            : ('float',  'Shiller', 'U.S. national nominal home price index (1890 base = 100)', 'index'),
    'real_hpi'               : ('float',  'Shiller', 'CPI-deflated real home price index', 'index'),
    'cpi_shiller'            : ('float',  'Shiller', 'CPI series used by Shiller for deflation', 'index'),
    'yoy_nominal'            : ('float',  'Shiller', 'Year-over-year % change in nominal HPI', '%'),
    'yoy_real'               : ('float',  'Shiller', 'Year-over-year % change in real HPI', '%'),
    'mortgage_rate_30yr'     : ('float',  'FRED',    '30-year fixed mortgage rate (MORTGAGE30US)', '% p.a.'),
    'unemployment_rate'      : ('float',  'FRED',    'U.S. national unemployment rate (UNRATE)', '%'),
    'cpi_all_items'          : ('float',  'FRED',    'CPI for all urban consumers (CPIAUCSL)', 'index'),
    'fed_funds_rate'         : ('float',  'FRED',    'Federal Funds effective rate (FEDFUNDS)', '% p.a.'),
    'treasury_10yr'          : ('float',  'FRED',    '10-year Treasury yield (GS10)', '% p.a.'),
    'case_shiller_national'  : ('float',  'FRED',    'Case-Shiller U.S. national HPI, SA (CSUSHPISA)', 'index'),
    'case_shiller_national_yoy': ('float','FRED',    'YoY % change in Case-Shiller national HPI', '%'),
    'mortgage_rate_chg'      : ('float',  'FRED',    'Annual change in 30yr mortgage rate', 'pp'),
}


def write_data_dictionary(df: pd.DataFrame, path: Path) -> None:
    """Write a markdown data dictionary for the final panel."""
    n_entities = df['fips'].nunique()
    n_years    = df['year'].nunique()
    year_min   = df['year'].min()
    year_max   = df['year'].max()

    lines = [
        "# Data Dictionary — Housing Disasters Panel\n",
        f"**Dataset:** `housing_disasters_panel.csv`  ",
        f"**Entities (counties):** {n_entities:,}  ",
        f"**Time periods (years):** {n_years} ({year_min}–{year_max})  ",
        f"**Total observations:** {len(df):,}  ",
        f"**Unit of analysis:** County × Year (long format)\n",
        "---\n",
        "## Variable Definitions\n",
        "| Variable | Type | Source | Description | Units |",
        "|---|---|---|---|---|",
    ]

    for col in df.columns:
        if col in DATA_DICTIONARY:
            dtype, source, desc, units = DATA_DICTIONARY[col]
        else:
            dtype  = str(df[col].dtype)
            source = 'Unknown'
            desc   = '—'
            units  = '—'
        lines.append(f"| `{col}` | {dtype} | {source} | {desc} | {units} |")

    lines += [
        "\n---\n",
        "## Cleaning Decisions\n",
        "| Decision | Justification |",
        "|---|---|",
        "| Aggregated SHELDUS event-level records to county-year | Unit of analysis is county-year; event multiplicity captured in `event_count` |",
        "| Filtered to 1980–2022 | SHELDUS coverage improves post-1980; Shiller/FRED series available throughout |",
        "| Log-transformed `total_damage` | Property damage is heavily right-skewed; log(damage+1) reduces influence of extreme events |",
        "| Left-joined Shiller + FRED on year | National macro series apply uniformly to all counties in a given year |",
        "| Dropped rows with missing FIPS or year | Cannot assign to panel without both keys |",
        "| Padded FIPS to 5 digits | Ensures consistent join keys across datasets |",
        "\n---\n",
        "## Sources\n",
        "- **SHELDUS**: Hazards & Vulnerability Research Institute, University of South Carolina. https://hazards.sc.edu/sheldus",
        "- **Shiller Data**: Robert J. Shiller, Yale University. https://shillerdata.com/",
        "- **FRED**: Federal Reserve Bank of St. Louis. https://fred.stlouisfed.org/",
    ]

    path.write_text('\n'.join(lines))
    print(f"✓ Data dictionary saved → {path}")


# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------

def main():
    print("=" * 60)
    print("Merge Final Analysis Panel")
    print("=" * 60)

    # ── Load processed datasets ───────────────────────────────────────────────
    print("\n[1] Loading processed datasets...")
    sheldus = load(SHELDUS_FILE, 'SHELDUS')
    shiller = load(SHILLER_FILE, 'Shiller')
    fred    = load(FRED_FILE,    'FRED')

    # ── Merge ─────────────────────────────────────────────────────────────────
    print("\n[2] Merging...")
    raw_panel = merge_panel(sheldus, shiller, fred)

    # ── Clean ─────────────────────────────────────────────────────────────────
    print("\n[3] Cleaning merged panel...")
    panel = clean_panel(raw_panel)

    # ── Verify ────────────────────────────────────────────────────────────────
    verify(panel)

    # ── Save panel ────────────────────────────────────────────────────────────
    panel.to_csv(OUT_PANEL, index=False)
    print(f"\n✓ Final panel saved → {OUT_PANEL}")
    print(f"  Shape: {panel.shape[0]:,} rows × {panel.shape[1]} columns")

    # ── Write data dictionary ─────────────────────────────────────────────────
    write_data_dictionary(panel, OUT_DICT)

    print("\n" + "=" * 60)
    print("Pipeline complete.")
    print(f"  Final panel:     {OUT_PANEL}")
    print(f"  Data dictionary: {OUT_DICT}")
    print("=" * 60)


if __name__ == '__main__':
    main()
