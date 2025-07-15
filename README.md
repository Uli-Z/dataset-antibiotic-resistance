# Clinical Antibiogram Dataset

This repository provides a curated and standardized dataset for creating and displaying clinical antibiograms.

## Purpose

The primary purpose of this dataset is to offer a clean, machine-readable data foundation for the automated generation of antibiograms (resistance charts). The data is structured for direct use in software applications, such as for visualizing antimicrobial resistance statistics.

It serves as a foundational dataset for other projects and is designed to be easily extendable with additional data sources.

## Data Origin and Processing

The data is aggregated from established public sources and has been standardized and manually curated for this purpose.

1.  **Core Data (Antibiotics, Organisms, Classes)**: The core definitions for antibiotics, microorganisms, and their classifications are derived from the **`AMR` R package**, which reflects scientific standards (including EUCAST). This data was exported and transformed into the CSV format for ease of use.
2.  **Resistance Data**: The surveillance statistics are sourced from the public reports of the **Antibiotic Resistance Surveillance (ARS)** system by the Robert Koch Institute (RKI), Germany.
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
    -   `amr_code`: Unique identifier for the antibiotic.
    -   `class`: The ID of the antibiotic class.
    -   `full_name_de`/`_en`: Full name in German/English.
    -   `short_name_de`/`_en`: Abbreviated name for display purposes.
    -   `synonyms_de`/`_en`: Common synonyms or trade names.
-   `organisms.csv`: Defines all microorganisms.
    -   `amr_code`: Unique identifier for the microorganism.
    -   `class_id`: The ID of the organism class.
    -   `full_name_de`/`_en`: Full name in German/English.
-   `antibiotic_classes.csv` & `organism_classes.csv`: Define the respective classes and their names.

### Data Sources and Resistance Data

-   `data_sources.csv`: The central manifest file describing the available resistance datasets.
    -   `id`: Unique ID for the dataset.
    -   `parent_id`: Defines the hierarchy (e.g., `de-nw-2023` is more specific than `de-ars-2023`), enabling the override logic.
    -   `name_de`/`_en`: Name of the dataset.
    -   `source_file`: The filename of the corresponding CSV file containing the resistance data.
-   **Resistance Files** (e.g., `resistance-rki-ars-nw-2023.csv`): Contain the actual data points.
    -   `antibiotic_id`: Foreign key to `amr_code` in `antibiotics.csv`.
    -   `organism_id`: Foreign key to `amr_code` in `organisms.csv`.
    -   `resistance_pct`: The percentage of resistant isolates.
    -   `n_isolates`: The total number of tested isolates.
-   `eucast_expected_resistance.csv`: Defines a baseline of expected (intrinsic) resistances according to EUCAST expert rules.

## Example Usage

The included Python script, `generate_html_report.py`, demonstrates how to consume the data. It reads one of the resistance files and the core data files to generate a standalone HTML report in a classic antibiogram layout (Organisms vs. Antibiotics).

To run the script:
```bash
python3 generate_html_report.py
```
This will create the file `ars_2023_germany_report.html` in the root directory.