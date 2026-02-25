"""
fetch_shiller_data.py
=====================
Downloads and cleans Robert Shiller's U.S. home price dataset.

Source:      https://shillerdata.com/
Data file:   http://www.econ.yale.edu/~shiller/data/Fig3-1.xls
             (historic U.S. home price index, CPI, real prices — annual back to 1890)

Downloads to: data/raw/shiller_raw.xls
Saves clean:  data/processed/shiller_clean.csv

Output columns:
  year          – calendar year (int)
  nominal_hpi   – nominal home price index (Shiller, Jan 1890 = 100)
  real_hpi      – CPI-deflated real home price index
  cpi           – consumer price index used by Shiller
  yoy_nominal   – year-over-year % change in nominal HPI
  yoy_real      – year-over-year % change in real HPI
"""

import sys
import requests
import pandas as pd
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from config_paths import RAW_DATA_DIR, PROCESSED_DATA_DIR

# -----------------------------------------------------------------------------
# File paths
# -----------------------------------------------------------------------------
RAW_FILE = RAW_DATA_DIR  / 'shiller_raw.xls'
OUT_FILE = PROCESSED_DATA_DIR / 'shiller_clean.csv'

# Primary download URL (Yale/Shiller)
SHILLER_URL = 'http://www.econ.yale.edu/~shiller/data/Fig3-1.xls'
SHILLER_URL_ALT = 'https://shillerdata.com/wp-content/uploads/Fig3-1.xlsx'


# -----------------------------------------------------------------------------
# Download
# -----------------------------------------------------------------------------

def download_raw(url: str, dest: Path) -> None:
    """Download Shiller XLS file if not already present."""
    if dest.exists():
        print(f"  Raw file already exists, skipping download: {dest.name}")
        return

    print(f"  Downloading from: {url}")
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    dest.write_bytes(response.content)
    print(f"  Saved → {dest}")


def try_download(dest: Path) -> None:
    """Try primary URL, fall back to alternate."""
    for url in [SHILLER_URL, SHILLER_URL_ALT]:
        try:
            download_raw(url, dest)
            return
        except Exception as e:
            print(f"  Warning: could not download from {url}: {e}")
    raise RuntimeError(
        "Could not download Shiller data from any URL.\n"
        f"  → Please download manually from https://shillerdata.com/\n"
        f"    and save as: {dest}"
    )


# -----------------------------------------------------------------------------
# Parse
# -----------------------------------------------------------------------------

def parse_xls(path: Path) -> pd.DataFrame:
    """
    Parse Shiller's Fig3-1.xls.

    The workbook has a 'Data' sheet. Relevant columns (by position or name):
      Col A: Date (decimal year, e.g. 2023.0 = Jan 2023, 2023.08 = Feb 2023)
      Col B: Home Price (nominal index)
      Col C: CPI
      Col D: Real Home Price (CPI-adjusted)
    """
    # Try reading the raw XLS — engine openpyxl handles .xlsx; xlrd for .xls
    try:
        xl = pd.ExcelFile(path, engine='xlrd')
    except Exception:
        xl = pd.ExcelFile(path, engine='openpyxl')

    # Find the data sheet
    sheet = 'Data' if 'Data' in xl.sheet_names else xl.sheet_names[0]
    print(f"  Reading sheet: '{sheet}'  |  available: {xl.sheet_names}")

    # Read with header on row 8 (Shiller's format; adjust if needed)
    for header_row in [7, 6, 8, 5, 0]:
        raw = xl.parse(sheet, header=header_row)
        # We need at least 4 columns and a date-like first column
        if raw.shape[1] >= 4:
            raw = raw.dropna(how='all')
            first_col = raw.iloc[:, 0]
            # Check if first column looks like decimal years
            numeric = pd.to_numeric(first_col, errors='coerce')
            valid = numeric.between(1880, 2030).sum()
            if valid > 50:
                print(f"  Detected header row: {header_row}")
                return raw

    raise ValueError(
        f"Could not parse {path}. "
        "Check that the file is Shiller's Fig3-1.xls with a 'Data' sheet."
    )


def clean(raw: pd.DataFrame) -> pd.DataFrame:
    """
    Clean and reshape Shiller data to annual observations.

    The Shiller Fig3-1.xls has multiple interleaved series with repeated date
    columns. Column layout (0-indexed):
      Col 0:  decimal date (monthly post-1953, annual pre-1953)
      Col 1:  nominal home price index (base 1890=100)
      Col 13: decimal date (BLS section)
      Col 14: CPI, BLS series (monthly, covers full modern range)

    Real HPI is computed as: nominal_hpi / cpi * cpi_base
    where cpi_base is the average CPI over 2000 (so real_hpi ≈ nominal_hpi
    in year-2000 dollars).

    Returns one row per year with nominal/real HPI and YoY changes.
    """
    # Extract date + nominal HPI (cols 0, 1)
    df = pd.DataFrame({
        'date_decimal': pd.to_numeric(raw.iloc[:, 0],  errors='coerce'),
        'nominal_hpi' : pd.to_numeric(raw.iloc[:, 1],  errors='coerce'),
        'cpi'         : pd.to_numeric(raw.iloc[:, 14], errors='coerce'),
    })

    df = df.dropna(subset=['date_decimal', 'nominal_hpi'])
    df['year'] = df['date_decimal'].astype(int)
    df = df[(df['year'] >= 1960) & (df['year'] <= 2024)]

    # Annual averages
    annual = (
        df.groupby('year')[['nominal_hpi', 'cpi']]
        .mean()
        .reset_index()
    )
    annual = annual.sort_values('year').reset_index(drop=True)

    # Compute real HPI: deflate nominal by CPI, re-base to year-2000 = 100
    cpi_2000 = annual.loc[annual['year'] == 2000, 'cpi']
    cpi_base = float(cpi_2000.iloc[0]) if not cpi_2000.empty else annual['cpi'].mean()
    annual['real_hpi'] = (annual['nominal_hpi'] / annual['cpi'] * cpi_base).round(4)

    # Year-over-year % changes
    annual['yoy_nominal'] = (annual['nominal_hpi'].pct_change() * 100).round(4)
    annual['yoy_real']    = (annual['real_hpi'].pct_change() * 100).round(4)

    for col in ['nominal_hpi', 'cpi']:
        annual[col] = annual[col].round(4)

    return annual


# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------

def main():
    print("=" * 60)
    print("Shiller Home Price Data Fetch & Clean")
    print("=" * 60)

    # Step 1: Download
    print("\n[1] Downloading raw data...")
    try_download(RAW_FILE)

    # Step 2: Parse XLS
    print("\n[2] Parsing XLS...")
    try:
        xl_install_hint = False
        raw = parse_xls(RAW_FILE)
    except ImportError:
        print("  xlrd not installed. Trying openpyxl fallback or installing xlrd...")
        import subprocess
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'xlrd', '-q'])
        raw = parse_xls(RAW_FILE)

    print(f"  Raw shape: {raw.shape}")

    # Step 3: Clean
    print("\n[3] Cleaning...")
    clean_df = clean(raw)

    before = raw.shape[0]
    after  = clean_df.shape[0]
    print(f"  Before: {before:,} rows (monthly) → After: {after:,} rows (annual)")
    print(f"  Year range: {clean_df['year'].min()} – {clean_df['year'].max()}")
    print(f"  Nominal HPI range: {clean_df['nominal_hpi'].min():.1f} – {clean_df['nominal_hpi'].max():.1f}")

    # Step 4: Save
    clean_df.to_csv(OUT_FILE, index=False)
    print(f"\n✓ Saved → {OUT_FILE}")

    print("\nSample output:")
    print(clean_df.tail(10).to_string(index=False))


if __name__ == '__main__':
    main()
