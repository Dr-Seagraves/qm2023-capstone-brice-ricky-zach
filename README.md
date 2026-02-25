[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/gp9US0IQ)
[![Open in Visual Studio Code](https://classroom.github.com/assets/open-in-vscode-2e0aaae1b6195c2367325f4f02e2d04e9abb55f0b24a779b69b11b9e10269abc.svg)](https://classroom.github.com/online_ide?assignment_repo_id=22634811&assignment_repo_type=AssignmentRepo)
# QM 2023 Capstone Project

Semester-long capstone for Statistics II: Data Analytics.

## Project Structure

- **code/** — Python scripts and notebooks. Use `config_paths.py` for paths.
- **data/raw/** — Original data (read-only)
- **data/processed/** — Intermediate cleaning outputs
- **data/final/** — M1 output: analysis-ready panel
- **results/figures/** — Visualizations
- **results/tables/** — Regression tables, summary stats
- **results/reports/** — Milestone memos
- **tests/** — Autograding test suite

Run `python code/config_paths.py` to verify paths.


Research Question: How do repeated natural disasters affect local housing price growth and volatility in
high-risk counties?
Datasets:
Dataset Source What It Provides
SHELDUS Open Dataset Catalog (OpenData_rows.csv, id
41; SHELDUS)
County-level disaster events, damages,
and fatalities
Shiller
Data
Open Dataset Catalog (OpenData_rows.csv, id
56; Shiller Data) Historical U.S. home price indices
FRED Openly available (FRED) via pandas-datareader
API Mortgage rates and local macro controls
Key Variables:
Outcome: County/metro home price growth and volatility
Driver: Disaster intensity (event count or loss amount)
Controls: Mortgage rates, unemployment, lagged home price trend
Groups: High-disaster vs. low-disaster regions
Why It's Interesting: Climate-related disasters are becoming more frequent and costly. This project tests
whether repeated disaster exposure creates persistent housing market discounts
