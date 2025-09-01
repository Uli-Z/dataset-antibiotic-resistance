# Clinical Antibiogram Dataset

<p align="center">
  <a href="https://uli-z.github.io/dataset-antibiotic-resistance/ars_2023_germany_report_all_en.html" style="display: inline-block; padding: 12px 24px; background-color: #238636; color: white; text-decoration: none; border-radius: 6px; font-weight: bold;">
    ➡️ View the Tabular Data Visualization
  </a>
</p>

This repository provides a curated and standardized dataset for creating and displaying clinical antibiograms.

## Purpose

The primary purpose of this dataset is to offer a clean, machine-readable data foundation for the automated generation of antibiograms (resistance charts). The data is structured for direct use in software applications, such as for visualizing antimicrobial resistance statistics.

It serves as a foundational dataset for other projects and is designed to be easily extendable with additional data sources.

## Data Origin and Processing

The data is aggregated from established public sources and has been standardized and manually curated for this purpose.

1.  **Core Data (Antibiotics, Organisms, Classes, Groups)**: The core definitions for antibiotics, microorganisms, and their classifications are derived from the **`AMR` R package**, which reflects scientific standards (including EUCAST). This data was exported and transformed into the CSV format for ease of use. Clinical and taxonomic groups were generated using custom R scripts.
2.  **Resistance Data**: The surveillance statistics are sourced from the public reports of the **Antibiotic Resistance Surveillance (ARS)** system by the Robert Koch Institute (RKI), Germany. This includes national summary data as well as regional data (e.g., for Northwest Germany), which was processed from raw Excel exports.
3.  **Standardization**: All entities (antibiotics, organisms) are linked via a uniform `amr_code`. This ensures data integrity and simplifies the process of extending the dataset with new sources (e.g., from other years, regions, or countries).

## Key Features

-   **Hierarchical Data Layering**: The `data_sources.csv` file defines a hierarchical tree of data sources. This structure allows an application to layer datasets, using general data (e.g., national averages) to fill gaps in more specific datasets (e.g., regional data). A "child" node's data is considered more specific and overrides the data from its "parent".
-   **Standardized Codes**: The universal use of `amr_code` ensures data integrity across all files.
-   **Multilingual Support**: All reference data includes identifiers in both German (`_de`) and English (`_en`), making it suitable for international applications.
-   **UI-Ready Abbreviations**: The dataset includes abbreviated short names (`short_name_de`, `short_name_en`) for antibiotics, ideal for use in space-constrained user interfaces.

## Dataset Structure

The dataset is split into several CSV files linked by IDs.

### Core Data

-   `antibiotics.csv`: Defines all antibiotics.
-   `organisms.csv`: Defines all microorganisms.
-   `organism_groups.csv`: Defines clinical or taxonomic groups for organisms.
-   `antibiotic_classes.csv` & `organism_classes.csv`: Define the respective classes.

### Data Sources and Resistance Data

-   `data_sources.csv`: The central manifest file describing the available resistance datasets.
-   **Resistance Files**: Contain the actual data points (`antibiotic_id`, `organism_id`, `resistance_pct`, `n_isolates`).
-   `eucast_expected_resistance.csv`: Defines a baseline of expected (intrinsic) resistances according to EUCAST expert rules.

*For a detailed description of the columns in each file, please refer to the file headers.*

## Scripts and Tools

This repository includes scripts to help process and extend the dataset.

### `aggregate_imports.py`

This Python script converts and aggregates raw data from the Excel files exported by the **ARS RKI online portal**. It processes multiple files, extracts the relevant resistance statistics, and formats them into a standardized CSV file compatible with this dataset's structure.

**Usage:**
```bash
python3 aggregate_imports.py 'path/to/your/excel_files/*.xlsx' -o output_filename.csv
```

**Dependencies:**
- Python 3 with the `pandas` and `openpyxl` libraries.
- R with the `AMR` library installed.
- The helper scripts `get_amr_code.R` and `get_antibiotic_amr_code.R` must be in the same directory.

### `generate_html_report.py`

This Python script demonstrates how to consume the data. It reads one of the resistance files and the core data files to generate a standalone HTML report in a classic antibiogram layout (Organisms vs. Antibiotics).

**Usage:**
```bash
python3 generate_html_report.py
```
This will create the file `ars_2023_germany_report_all_en.html` in the root directory.
