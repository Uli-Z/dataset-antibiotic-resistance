import pandas as pd
import glob
import subprocess
import re
import sys
import argparse

def get_amr_code(name, script_path):
    """Calls an R script to get the AMR code for a given name."""
    try:
        # Clean up names like "Cefepim (Non-meningitis)" before sending to R
        cleaned_name = re.sub(r'\s*\(.*\)', '', name).strip()
        result = subprocess.run(
            ['Rscript', script_path, cleaned_name],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"  ERROR: Could not get AMR code for '{name}'. Details: {e.stderr.strip()}", file=sys.stderr)
        return None

def parse_resistance_value(value):
    """Converts a string like '8,4' to a float 8.4."""
    if isinstance(value, str):
        value = value.strip().replace(',', '.')
        if '-' in value:
            parts = [float(p.strip()) for p in value.split('-')]
            return sum(parts) / len(parts)
        return float(value)
    return float(value)

def process_excel_file(file_path):
    """Processes a single Excel file and extracts resistance data."""
    print(f"\n--- Processing {file_path} ---")
    df = pd.read_excel(file_path, header=None)
    
    organism_name = None
    for index, row in df.iterrows():
        if str(row.get(0)) == 'Erreger:':
            organism_name = str(row.get(2, '')).strip()
            break
    
    if not organism_name:
        print(f"  WARNING: Could not find organism name in {file_path}", file=sys.stderr)
        return []

    organism_id = get_amr_code(organism_name, 'get_amr_code.R')
    if not organism_id:
        print(f"  WARNING: Skipping file due to missing organism AMR code for '{organism_name}'.", file=sys.stderr)
        return []
    print(f"  Found Organism: '{organism_name}' -> AMR Code: '{organism_id}'")

    header_row_index = -1
    header_map = {}
    for index, row in df.iterrows():
        row_values = list(row)
        if 'N' in row_values and 'S %' in row_values and 'R %' in row_values:
            header_row_index = index
            header_map = {val: i for i, val in enumerate(row_values) if pd.notna(val)}
            break
            
    if header_row_index == -1:
        print(f"  WARNING: Could not find data table header in {file_path}. Skipping.", file=sys.stderr)
        return []

    col_antibiotic = 0
    col_n = header_map.get('N')
    col_r_pct = header_map.get('R %')

    if col_n is None or col_r_pct is None:
        print(f"  WARNING: Could not map 'N' or 'R %' columns. Skipping.", file=sys.stderr)
        return []

    extracted_data = []
    for index, row in df.iloc[header_row_index + 1:].iterrows():
        antibiotic_name = row.get(col_antibiotic)
        n_isolates = row.get(col_n)
        resistance_pct_val = row.get(col_r_pct)

        if isinstance(antibiotic_name, str) and antibiotic_name.startswith('    ') and pd.notna(n_isolates) and pd.notna(resistance_pct_val):
            antibiotic_name = antibiotic_name.strip()
            if not antibiotic_name: continue

            antibiotic_id = get_amr_code(antibiotic_name, 'get_antibiotic_amr_code.R')
            
            if not antibiotic_id:
                print(f"    - Could not get AMR code for antibiotic '{antibiotic_name}'. Skipping entry.")
                continue

            try:
                n_isolates_clean = int(str(n_isolates).replace('.', ''))
                
                extracted_data.append({
                    'organism_id': organism_id,
                    'antibiotic_id': antibiotic_id,
                    'resistance_pct': parse_resistance_value(resistance_pct_val),
                    'n_isolates': n_isolates_clean
                })
            except (ValueError, TypeError) as e:
                print(f"    - Could not parse data for '{antibiotic_name}'. N='{n_isolates}', R%='{resistance_pct_val}'. Error: {e}. Skipping entry.")

    print(f"  Successfully extracted {len(extracted_data)} data points from this file.")
    return extracted_data

def main():
    """Main function to aggregate data from all Excel files."""
    parser = argparse.ArgumentParser(description="Aggregate antimicrobial resistance data from Excel files.")
    parser.add_argument('input_files', nargs='+', help="List of input Excel files or a glob pattern (e.g., 'import/*.xlsx').")
    parser.add_argument('-o', '--output', required=True, help="Path to the output CSV file.")
    args = parser.parse_args()

    all_data = []
    
    # Expand glob patterns and create a unique, sorted list of files
    excel_files = sorted(list(set(f for pattern in args.input_files for f in glob.glob(pattern))))

    if not excel_files:
        print(f"Error: No files found matching the pattern(s): {', '.join(args.input_files)}", file=sys.stderr)
        sys.exit(1)

    for file_path in excel_files:
        all_data.extend(process_excel_file(file_path))
        
    print("\n--- Aggregation Summary ---")
    if not all_data:
        print("No data was extracted. Exiting.")
        return

    final_df = pd.DataFrame(all_data)
    
    column_order = ['organism_id', 'antibiotic_id', 'resistance_pct', 'n_isolates']
    final_df = final_df[column_order]

    final_df.to_csv(args.output, index=False)
    
    print(f"Processed {len(excel_files)} files.")
    print(f"Aggregated a total of {len(final_df)} data points.")
    print(f"Successfully saved aggregated data to '{args.output}'")

if __name__ == "__main__":
    main()