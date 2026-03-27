"""
Capstone Project - Centralized Path Configuration
==================================================

This module provides centralized path management for the capstone project.
Import this at the top of every script to ensure consistent, relative paths.

Usage:
    from config_paths import RAW_DATA_DIR, FINAL_DATA_DIR, FIGURES_DIR, TABLES_DIR

    df = pd.read_csv(RAW_DATA_DIR / 'my_data.csv')
    merged.to_csv(FINAL_DATA_DIR / 'analysis_panel.csv', index=False)
    plt.savefig(FIGURES_DIR / 'my_plot.png', dpi=300)
"""

from pathlib import Path
import sys

# ==============================================================================
# PROJECT ROOT DETECTION
# ==============================================================================

def _is_project_root(path: Path) -> bool:
    """Return True when the path looks like the capstone project root."""
    required_dirs = ['code', 'data', 'results']
    required_files = ['README.md']
    return all((path / d).is_dir() for d in required_dirs) and all((path / f).exists() for f in required_files)


def find_project_root():
    """
    Find project root by looking for key indicators.
    Searches upward from current file location.
    """
    current = Path(__file__).resolve().parent

    # Search upward from code/ to find a directory with expected project structure.
    search_candidates = [current] + list(current.parents[:5])
    for candidate in search_candidates:
        if _is_project_root(candidate):
            return candidate

    # Fallback: assume parent of code/ is project root (when config_paths lives in code/)
    return current.parent

PROJECT_ROOT = find_project_root()

# ==============================================================================
# DIRECTORY PATHS
# ==============================================================================

# Code directory
CODE_DIR = PROJECT_ROOT / 'code'

# Data directories
DATA_DIR = PROJECT_ROOT / 'data'
RAW_DATA_DIR = DATA_DIR / 'raw'
PROCESSED_DATA_DIR = DATA_DIR / 'processed'
FINAL_DATA_DIR = DATA_DIR / 'final'

# Results directories
RESULTS_DIR = PROJECT_ROOT / 'results'
FIGURES_DIR = RESULTS_DIR / 'figures'
TABLES_DIR = RESULTS_DIR / 'tables'
REPORTS_DIR = RESULTS_DIR / 'reports'

# ==============================================================================
# DIRECTORY CREATION
# ==============================================================================

def ensure_directories(verbose=False):
    """Create all necessary directories if they don't exist."""
    directories = [
        CODE_DIR,
        RAW_DATA_DIR,
        PROCESSED_DATA_DIR,
        FINAL_DATA_DIR,
        FIGURES_DIR,
        TABLES_DIR,
        REPORTS_DIR
    ]

    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)

    if verbose:
        print(f"Project structure verified at: {PROJECT_ROOT}")

# Auto-create directories on import
ensure_directories()

# ==============================================================================
# UTF-8 ENCODING (Windows PowerShell fix)
# ==============================================================================

if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

# ==============================================================================
# VERIFICATION
# ==============================================================================

if __name__ == "__main__":
    """Run this script to verify path configuration."""
    try:
        from rich.console import Console
        from rich.table import Table
        console = Console()
        table = Table(title="Capstone Project Path Configuration", show_header=True)
        table.add_column("Variable", style="cyan", no_wrap=True)
        table.add_column("Path", style="green")
        table.add_column("Exists?", style="yellow")

        paths = {
            'PROJECT_ROOT': PROJECT_ROOT,
            'CODE_DIR': CODE_DIR,
            'DATA_DIR': DATA_DIR,
            'RAW_DATA_DIR': RAW_DATA_DIR,
            'PROCESSED_DATA_DIR': PROCESSED_DATA_DIR,
            'FINAL_DATA_DIR': FINAL_DATA_DIR,
            'RESULTS_DIR': RESULTS_DIR,
            'FIGURES_DIR': FIGURES_DIR,
            'TABLES_DIR': TABLES_DIR,
            'REPORTS_DIR': REPORTS_DIR,
        }

        for name, path in paths.items():
            exists = "\u2713" if path.exists() else "\u2717"
            table.add_row(name, str(path), exists)

        console.print(table)
        console.print("\n[bold green]All paths verified![/bold green]")
    except ImportError:
        for name, path in [('PROJECT_ROOT', PROJECT_ROOT), ('RAW_DATA_DIR', RAW_DATA_DIR),
                          ('FINAL_DATA_DIR', FINAL_DATA_DIR), ('FIGURES_DIR', FIGURES_DIR),
                          ('TABLES_DIR', TABLES_DIR)]:
            print(f"  {name}: {path} ({'exists' if path.exists() else 'missing'})")
        print("\nAll paths verified.")
