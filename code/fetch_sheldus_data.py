"""
fetch_sheldus_data.py
=====================
Downloads and cleans NOAA Storm Events county-level natural disaster data.
Used as a direct substitute for SHELDUS (same variables: property damage,
crop damage, injuries, fatalities, by county and year).

Source: NOAA National Centers for Environmental Information (NCEI)
URL:    https://www.ncei.noaa.gov/pub/data/swdi/stormevents/csvfiles/
Access: Fully public — no account or API key required.

Downloads 'details' CSV files for each year (1960-present), concatenates
them, aggregates to county-year level, and saves:
  -> data/raw/sheldus_raw.csv          (combined raw event-level data)
  -> data/processed/sheldus_clean.csv  (county-year panel)
"""

import io
import sys
import gzip
import re
import time
import warnings
import requests
import pandas as pd
from pathlib import Path

warnings.filterwarnings('ignore')

sys.path.insert(0, str(Path(__file__).resolve().parent))
from config_paths import RAW_DATA_DIR, PROCESSED_DATA_DIR

# -----------------------------------------------------------------------------
# Config
# -----------------------------------------------------------------------------
START_YEAR = 1960
END_YEAR   = 2024
NOAA_BASE  = 'https://www.ncei.noaa.gov/pub/data/swdi/stormevents/csvfiles/'
RAW_FILE   = RAW_DATA_DIR       / 'sheldus_raw.csv'
OUT_FILE   = PROCESSED_DATA_DIR / 'sheldus_clean.csv'

DAMAGE_MULTIPLIERS = {'K': 1_000, 'M': 1_000_000, 'B': 1_000_000_000}


# -----------------------------------------------------------------------------
# Step 1: Discover available filenames from NOAA directory listing
# -----------------------------------------------------------------------------

def get_noaa_file_index() -> dict:
    """
    Scrape the NOAA directory and return {year: filename} for details files.
    If a year appears multiple times (different creation dates), the last
    entry (most recently created) wins.
    """
    resp = requests.get(NOAA_BASE, timeout=30)
    resp.raise_for_status()
    pattern = re.compile(r'StormEvents_details-ftp_v1\.0_d(\d{4})_c\d+\.csv\.gz')
    index = {}
    for match in re.finditer(r'(StormEvents_details-ftp_v1\.0_d\d{4}_c\d+\.csv\.gz)', resp.text):
        fname = match.group(1)
        year  = int(re.search(r'_d(\d{4})_', fname).group(1))
        index[year] = fname   # newest wins (last occurrence in listing)
    return index


# -----------------------------------------------------------------------------
# Step 2: Download + parse one year
# -----------------------------------------------------------------------------

def parse_damage(val) -> float:
    """Convert NOAA damage strings ('10K', '2.5M', '1B', etc.) to float USD."""
    if pd.isna(val) or str(val).strip() in ('', '0'):
        return 0.0
    s = str(val).strip().upper()
    if s[-1] in DAMAGE_MULTIPLIERS:
        try:
            return float(s[:-1]) * DAMAGE_MULTIPLIERS[s[-1]]
        except ValueError:
            return 0.0
    try:
        return float(s)
    except ValueError:
        return 0.0


def fetch_year(year: int, filename: str) -> pd.DataFrame:
    """Download and parse one year of NOAA Storm Events details."""
    url = NOAA_BASE + filename
    try:
        resp = requests.get(url, timeout=90)
        resp.raise_for_status()
        with gzip.open(io.BytesIO(resp.content), 'rt', encoding='latin-1') as f:
            df = pd.read_csv(f, low_memory=False)

        # Keep only county-level records (CZ_TYPE == 'C')
        if 'CZ_TYPE' in df.columns:
            df = df[df['CZ_TYPE'] == 'C'].copy()

        # Build 5-digit FIPS from state + county FIPS
        df['state_fips'] = pd.to_numeric(df.get('STATE_FIPS', pd.Series(dtype=float)), errors='coerce')
        df['cz_fips']    = pd.to_numeric(df.get('CZ_FIPS',    pd.Series(dtype=float)), errors='coerce')
        df = df.dropna(subset=['state_fips', 'cz_fips'])
        df['fips'] = (
            df['state_fips'].astype(int).astype(str).str.zfill(2) +
            df['cz_fips'].astype(int).astype(str).str.zfill(3)
        )

        df['year']            = year
        df['property_damage'] = df.get('DAMAGE_PROPERTY', pd.Series(0, index=df.index)).apply(parse_damage)
        df['crop_damage']     = df.get('DAMAGE_CROPS',    pd.Series(0, index=df.index)).apply(parse_damage)
        df['injuries']        = (
            pd.to_numeric(df.get('INJURIES_DIRECT',   0), errors='coerce').fillna(0) +
            pd.to_numeric(df.get('INJURIES_INDIRECT', 0), errors='coerce').fillna(0)
        )
        df['fatalities']      = (
            pd.to_numeric(df.get('DEATHS_DIRECT',   0), errors='coerce').fillna(0) +
            pd.to_numeric(df.get('DEATHS_INDIRECT', 0), errors='coerce').fillna(0)
        )
        df['hazard_type'] = df.get('EVENT_TYPE', pd.Series('', index=df.index))
        df['state']       = df.get('STATE',      pd.Series('', index=df.index))

        keep = ['fips', 'state', 'year', 'hazard_type',
                'property_damage', 'crop_damage', 'injuries', 'fatalities']
        result = df[[c for c in keep if c in df.columns]].copy()

        print(f"  + {year}  {len(result):>7,} county events")
        time.sleep(0.1)
        return result

    except Exception as e:
        print(f"  x {year}  failed: {e}")
        return pd.DataFrame()


# -----------------------------------------------------------------------------
# Step 3: Aggregate to county-year panel
# -----------------------------------------------------------------------------

def aggregate_county_year(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate event-level records to one row per (fips, year)."""
    df = df.copy()
    df['total_damage'] = df['property_damage'] + df['crop_damage']

    panel = df.groupby(['fips', 'year']).agg(
        event_count      = ('fips',            'count'),
        total_damage     = ('total_damage',     'sum'),
        property_damage  = ('property_damage',  'sum'),
        crop_damage      = ('crop_damage',      'sum'),
        total_injuries   = ('injuries',         'sum'),
        total_fatalities = ('fatalities',       'sum'),
    ).reset_index()

    panel = panel.sort_values(['fips', 'year']).reset_index(drop=True)

    for col in panel.select_dtypes('float').columns:
        panel[col] = panel[col].round(2)

    return panel


# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------

def main():
    print("=" * 60)
    print("NOAA Storm Events -- Fetch & Clean (SHELDUS substitute)")
    print("=" * 60)
    print(f"  Year range: {START_YEAR} - {END_YEAR}")

    print("\n[1] Fetching NOAA directory listing...")
    index = get_noaa_file_index()
    years = sorted(y for y in index if START_YEAR <= y <= END_YEAR)
    print(f"  Found {len(years)} year files ({years[0]}-{years[-1]})")

    print(f"\n[2] Downloading {len(years)} year files from NOAA...")
    frames = []
    for yr in years:
        df = fetch_year(yr, index[yr])
        if not df.empty:
            frames.append(df)

    if not frames:
        raise RuntimeError("No data downloaded. Check your internet connection.")

    raw = pd.concat(frames, ignore_index=True)
    print(f"\n  Combined raw shape: {raw.shape}")

    raw.to_csv(RAW_FILE, index=False)
    print(f"  Saved raw -> {RAW_FILE}")

    print("\n[3] Aggregating to county-year panel...")
    panel = aggregate_county_year(raw)
    print(f"  Panel shape: {panel.shape}")
    print(f"  Counties:    {panel['fips'].nunique():,}")
    print(f"  Years:       {panel['year'].min()} - {panel['year'].max()}")
    print(f"  Avg events/county-year: {panel['event_count'].mean():.2f}")

    print("\n[4] Summary statistics:")
    print(panel.describe().T[['count', 'mean', 'min', 'max']].round(2).to_string())

    panel.to_csv(OUT_FILE, index=False)
    print(f"\nSaved -> {OUT_FILE}")

    print("\nSample output (first 10 rows):")
    print(panel.head(10).to_string(index=False))


if __name__ == '__main__':
    main()
