"""
fetch_fred_data.py
==================
Downloads macro control variables from FRED (Federal Reserve Economic Data)
using direct REST API calls (no pandas-datareader dependency).

A free FRED API key is required. Get one at:
  https://fred.stlouisfed.org/docs/api/api_key.html  (takes ~1 minute)

Set your key one of two ways:
  Option A (environment variable — recommended):
      export FRED_API_KEY="your_key_here"
  Option B (paste directly in this file):
      FRED_API_KEY_FALLBACK = "your_key_here"

Series downloaded:
  MORTGAGE30US  – 30-year fixed mortgage rate (weekly, Freddie Mac)
  UNRATE        – U.S. national unemployment rate (monthly, BLS)
  CPIAUCSL      – CPI all items (monthly, BLS) — used for inflation adjustment
  FEDFUNDS      – Federal Funds effective rate (monthly)
  GS10          – 10-year Treasury yield (monthly)
  CSUSHPISA     – Case-Shiller U.S. National HPI, seasonally adjusted (monthly)

Saves:
  data/raw/fred_raw.csv
  data/processed/fred_clean.csv  ← annual averages, one row per year
"""

import os
import sys
import time
import warnings
import requests
import pandas as pd
from pathlib import Path
from datetime import date

warnings.filterwarnings('ignore')

sys.path.insert(0, str(Path(__file__).resolve().parent))
from config_paths import RAW_DATA_DIR, PROCESSED_DATA_DIR

# -----------------------------------------------------------------------------
# Config
# -----------------------------------------------------------------------------
START_DATE = '1960-01-01'
END_DATE   = date.today().strftime('%Y-%m-%d')

# ── Paste your free FRED API key here if not using an env variable ────────────
FRED_API_KEY_FALLBACK = "3cb2bba4cae14b3afd374c31bb682272"   # e.g. "abcdef1234567890abcdef1234567890"

FRED_SERIES = {
    'MORTGAGE30US' : 'mortgage_rate_30yr',    # % per annum
    'UNRATE'       : 'unemployment_rate',     # %
    'CPIAUCSL'     : 'cpi_all_items',         # index
    'FEDFUNDS'     : 'fed_funds_rate',        # %
    'GS10'         : 'treasury_10yr',         # %
    'CSUSHPISA'    : 'case_shiller_national', # index
}

FRED_API_BASE = 'https://api.stlouisfed.org/fred/series/observations'

RAW_FILE = RAW_DATA_DIR       / 'fred_raw.csv'
OUT_FILE = PROCESSED_DATA_DIR / 'fred_clean.csv'


# -----------------------------------------------------------------------------
# Resolve API key
# -----------------------------------------------------------------------------

def get_api_key() -> str:
    """Return FRED API key from env or fallback constant."""
    key = os.environ.get('FRED_API_KEY', '').strip() or FRED_API_KEY_FALLBACK.strip()
    if not key:
        raise EnvironmentError(
            "\n[ERROR] FRED API key not found.\n"
            "  → Get a free key at: https://fred.stlouisfed.org/docs/api/api_key.html\n"
            "  → Then either:\n"
            "       export FRED_API_KEY='your_key'      (in terminal before running)\n"
            "    or paste it in FRED_API_KEY_FALLBACK in this file.\n"
        )
    return key


# -----------------------------------------------------------------------------
# Download from FRED REST API
# -----------------------------------------------------------------------------

def fetch_fred_series(series_id: str, rename: str, api_key: str) -> pd.Series:
    """Download a single FRED series via REST API."""
    params = {
        'series_id'    : series_id,
        'api_key'      : api_key,
        'file_type'    : 'json',
        'observation_start': START_DATE,
        'observation_end'  : END_DATE,
    }
    try:
        resp = requests.get(FRED_API_BASE, params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()

        if 'observations' not in data:
            raise ValueError(f"Unexpected response: {list(data.keys())}")

        obs = data['observations']
        df = pd.DataFrame(obs)[['date', 'value']]
        df['date']  = pd.to_datetime(df['date'])
        df['value'] = pd.to_numeric(df['value'], errors='coerce')
        s = df.set_index('date')['value'].rename(rename)
        s = s.dropna()

        print(f"  ✓ {series_id:<20} → {rename:<30} ({len(s):,} obs)")
        time.sleep(0.15)   # be polite to the API
        return s

    except Exception as e:
        print(f"  ✗ {series_id:<20} failed: {e}")
        return pd.Series(dtype=float, name=rename)


def fetch_all(api_key: str) -> pd.DataFrame:
    """Download all FRED series and combine into a single wide DataFrame."""
    frames = []
    for series_id, col_name in FRED_SERIES.items():
        s = fetch_fred_series(series_id, col_name, api_key)
        if not s.empty:
            frames.append(s)

    if not frames:
        raise RuntimeError("No FRED series could be downloaded. Check your API key.")

    df = pd.concat(frames, axis=1)
    df.index.name = 'date'
    df = df.reset_index()
    df['date'] = pd.to_datetime(df['date'])
    return df


# -----------------------------------------------------------------------------
# Aggregate to annual
# -----------------------------------------------------------------------------

def to_annual(df: pd.DataFrame) -> pd.DataFrame:
    """
    Average all monthly/weekly series to annual observations.
    Returns one row per year.
    """
    df['year'] = df['date'].dt.year
    numeric_cols = [c for c in df.columns if c not in ('date', 'year')]

    annual = (
        df.groupby('year')[numeric_cols]
        .mean()
        .reset_index()
    )

    # Year-over-year changes for key series
    annual = annual.sort_values('year').reset_index(drop=True)

    for col in ['case_shiller_national', 'cpi_all_items']:
        if col in annual.columns:
            annual[f'{col}_yoy'] = annual[col].pct_change() * 100

    if 'mortgage_rate_30yr' in annual.columns:
        annual['mortgage_rate_chg'] = annual['mortgage_rate_30yr'].diff()

    # Round
    for col in annual.select_dtypes('float').columns:
        annual[col] = annual[col].round(4)

    # Keep only years with at least some data
    annual = annual.dropna(subset=[c for c in numeric_cols if c in annual.columns], how='all')

    return annual


# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------

def main():
    print("=" * 60)
    print("FRED Macro Data Fetch & Clean")
    print("=" * 60)
    print(f"  Date range: {START_DATE} → {END_DATE}")
    print(f"  Series:     {len(FRED_SERIES)}")

    # ── Resolve API key ───────────────────────────────────────────────────────
    api_key = get_api_key()
    print(f"  API key:    {'*' * (len(api_key) - 4) + api_key[-4:]}")

    # ── Step 1: Download ─────────────────────────────────────────────────────
    print("\n[1] Fetching from FRED...")
    raw = fetch_all(api_key)
    print(f"\n  Combined raw shape: {raw.shape}")

    # Save raw
    raw.to_csv(RAW_FILE, index=False)
    print(f"  Saved raw → {RAW_FILE}")

    # ── Step 2: Aggregate to annual ──────────────────────────────────────────
    print("\n[2] Aggregating to annual...")
    annual = to_annual(raw)

    print(f"  Annual shape: {annual.shape}")
    print(f"  Year range:   {annual['year'].min()} – {annual['year'].max()}")

    # ── Step 3: Summary stats ─────────────────────────────────────────────────
    print("\n[3] Summary statistics:")
    print(annual.describe().T[['count', 'mean', 'min', 'max']].round(2).to_string())

    # ── Step 4: Save ──────────────────────────────────────────────────────────
    annual.to_csv(OUT_FILE, index=False)
    print(f"\n✓ Saved → {OUT_FILE}")

    print("\nSample output (last 10 years):")
    print(annual.tail(10).to_string(index=False))


if __name__ == '__main__':
    main()
