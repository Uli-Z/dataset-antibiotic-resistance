

import pandas as pd
from pathlib import Path
from collections import defaultdict

# --- Configuration ---
TARGET_DATA_ID = "de-ars-2023-all"
OUTPUT_HTML_BASE_NAME = "ars_2023_germany_report_all"
LANGUAGES = ["de", "en"]

# --- File Paths ---
BASE_DIR = Path(__file__).parent
DATA_SOURCES_FILE = BASE_DIR / "data_sources.csv"
ANTIBIOTICS_FILE = BASE_DIR / "antibiotics.csv"
ORGANISMS_FILE = BASE_DIR / "organisms.csv"
ANTIBIOTIC_CLASSES_FILE = BASE_DIR / "antibiotic_classes.csv"
ORGANISM_CLASSES_FILE = BASE_DIR / "organism_classes.csv"

# --- Helper Functions ---

def get_path_to_target(sources_df, target_id):
    path = []
    current_id = target_id
    while current_id and not pd.isna(current_id):
        node = sources_df[sources_df['id'] == current_id]
        if node.empty: return None
        path.append(node.iloc[0])
        current_id = node.iloc[0]['parent_id']
    return path[::-1]

def get_resistance_color(value):
    if pd.isna(value): return "#f0f0f0"
    if value >= 100: return "#a50026"
    if value >= 20: return "#d73027"
    if value >= 10: return "#fee08b"
    return "#1a9850"

def generate_html(df_pivot, antibiotics_map, organisms_map, ab_classes_map, org_classes_map, language='en'):
    lang_suffix = f"_{language}"
    texts = {
        "de": {"title": "Antibiogramm Report", "header": "Antibiogramm", "sub_header": "Resistenzrate (%)", "antibiotic_col": "Antibiotikum", "legend_header": "Legende", "legend_intrinsic": "Erwartete (intrinsische) Resistenz", "legend_high": "Hohe Resistenzrate (&ge;20%)", "legend_medium": "Mittlere Resistenzrate (10% &ndash; 19%)", "legend_low": "Niedrige Resistenzrate (<10%)", "legend_nodata": "Keine Daten"},
        "en": {"title": "Antibiogram Report", "header": "Antibiogram", "sub_header": "Resistance Rate (%)", "antibiotic_col": "Antibiotic", "legend_header": "Legend", "legend_intrinsic": "Expected (intrinsic) Resistance", "legend_high": "High Resistance Rate (&ge;20%)", "legend_medium": "Medium Resistance Rate (10% &ndash; 19%)", "legend_low": "Low Resistance Rate (<10%)", "legend_nodata": "No data"}
    }
    t = texts[language]

    html = f"""
    <!DOCTYPE html><html lang="{language}"><head><meta charset="UTF-8"><title>{t['title']}</title>
    <style>
        body {{ font-family: sans-serif; margin: 2em; }} h1 {{ color: #333; }}
        table {{ border-collapse: collapse; font-size: 0.8em; table-layout: auto; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: center; }}
        .antibiotic-col {{ text-align: left; white-space: nowrap; }}
        th.ab-class-header, th.org-class-header {{ background-color: #f2f2f2; text-align: left; font-weight: bold;}}
        th.org-superclass-header {{ background-color: #e0e0e0; font-weight: bold; }}
        .organism-name {{ writing-mode: vertical-rl; text-orientation: mixed; white-space: nowrap; font-size: 0.9em; }}
        .color-box {{ width: 12px; height: 12px; display: inline-block; border: 1px solid #ccc; }}
    </style></head><body><h1>{t['header']}</h1><p>{t['sub_header']}</p>
    """
    html += "<table><thead>"

    # --- Organism Super-Class Header (e.g., Gram-positive) ---
    html += f"<tr><th class='antibiotic-col'></th>"
    org_superclasses = defaultdict(int)
    for org_code in df_pivot.columns:
        org_class_id = organisms_map[org_code]['class_id']
        super_class_id = org_classes_map[org_class_id]['parent_id']
        org_superclasses[super_class_id] += 1
    for super_id, colspan in org_superclasses.items():
        super_name = org_classes_map[super_id][f'name{lang_suffix}']
        html += f"<th colspan='{colspan}' class='org-superclass-header'>{super_name}</th>"
    html += "</tr>"

    # --- Organism Class Header (e.g., Enterobacterales) ---
    html += f"<tr><th class='antibiotic-col'>{t['antibiotic_col']}</th>"
    org_classes = defaultdict(int)
    for org_code in df_pivot.columns:
        org_class_id = organisms_map[org_code]['class_id']
        org_classes[org_class_id] += 1
    for class_id, colspan in org_classes.items():
        class_name = org_classes_map[class_id][f'name{lang_suffix}']
        html += f"<th colspan='{colspan}' class='org-class-header'>{class_name}</th>"
    html += "</tr>"
    
    # --- Organism Name Header ---
    html += f"<tr><th class='antibiotic-col'></th>"
    for org_code in df_pivot.columns:
        org_name = organisms_map[org_code].get(f'full_name{lang_suffix}', org_code)
        html += f"<th><div class='organism-name'>{org_name}</div></th>"
    html += "</tr></thead>"

    # --- Table Body ---
    html += "<tbody>"
    current_ab_class_id = None
    for ab_code, row in df_pivot.iterrows():
        ab_class_id = antibiotics_map[ab_code]['class']
        if ab_class_id != current_ab_class_id:
            current_ab_class_id = ab_class_id
            class_name = ab_classes_map.get(ab_class_id, {}).get(f'name{lang_suffix}', ab_class_id)
            html += f"<tr><th colspan='{len(df_pivot.columns) + 1}' class='ab-class-header'>{class_name}</th></tr>"
        ab_name = antibiotics_map[ab_code].get(f'full_name{lang_suffix}', ab_code)
        html += f"<tr><td class='antibiotic-col'>{ab_name}</td>"
        for org_code in df_pivot.columns:
            value = row[org_code]
            color = get_resistance_color(value)
            text_color = "#ffffff" if color in ["#a50026", "#d73027"] else "#000000"
            display_val = f"{value:.0f}" if pd.notna(value) and value < 100 else ""
            if value >= 100: display_val = "R"
            html += f"<td style='background-color: {color}; color: {text_color};'>{display_val}</td>"
        html += "</tr>"
    html += "</tbody></table>"
    
    html += f"""
        <h2>{t['legend_header']}</h2><table>
            <tr><td style="width: 30px;"><div class="color-box" style="background-color: #a50026;"></div></td><td>{t['legend_intrinsic']}</td></tr>
            <tr><td><div class="color-box" style="background-color: #d73027;"></div></td><td>{t['legend_high']}</td></tr>
            <tr><td><div class="color-box" style="background-color: #fee08b;"></div></td><td>{t['legend_medium']}</td></tr>
            <tr><td><div class="color-box" style="background-color: #1a9850;"></div></td><td>{t['legend_low']}</td></tr>
            <tr><td><div class="color-box" style="background-color: #f0f0f0;"></div></td><td>{t['legend_nodata']}</td></tr>
        </table></body></html>
    """
    return html

# --- Main Execution ---

def main():
    # Load all data from CSVs
    data_sources_df = pd.read_csv(DATA_SOURCES_FILE)
    antibiotics_df = pd.read_csv(ANTIBIOTICS_FILE)
    organisms_df = pd.read_csv(ORGANISMS_FILE)
    ab_classes_df = pd.read_csv(ANTIBIOTIC_CLASSES_FILE)
    org_classes_df = pd.read_csv(ORGANISM_CLASSES_FILE)

    # Create maps for easy lookup
    antibiotics_map = antibiotics_df.set_index('amr_code').to_dict('index')
    organisms_map = organisms_df.set_index('amr_code').to_dict('index')
    ab_classes_map = ab_classes_df.set_index('id').to_dict('index')
    org_classes_map = org_classes_df.set_index('id').to_dict('index')

    path_to_target = get_path_to_target(data_sources_df, TARGET_DATA_ID)
    if not path_to_target:
        print(f"Error: Target ID '{TARGET_DATA_ID}' not found.")
        return

    print(f"Generating report for: {path_to_target[-1]['name_en']}")
    all_dfs = []
    for node in path_to_target:
        source_file = BASE_DIR / node['source_file']
        if not source_file.exists():
            print(f"Warning: File {source_file.name} not found. Skipping.")
            continue
        df = pd.read_csv(source_file)
        df.rename(columns={'antibiotic_id': 'antibiotic_code', 'organism_id': 'organism_code'}, inplace=True)
        if 'resistance_pct' not in df.columns: df['resistance_pct'] = 100.0
        all_dfs.append(df[['organism_code', 'antibiotic_code', 'resistance_pct']])

    if not all_dfs:
        print("No dataframes loaded. Exiting.")
        return
        
    merged_df = pd.concat(all_dfs).drop_duplicates(subset=['organism_code', 'antibiotic_code'], keep='last')
    df_pivot = merged_df.pivot_table(index='antibiotic_code', columns='organism_code', values='resistance_pct')

    # Sort rows (antibiotics)
    antibiotics_df['class_cat'] = pd.Categorical(antibiotics_df['class'], categories=ab_classes_df['id'].tolist(), ordered=True)
    sorted_antibiotics = antibiotics_df.sort_values(by=['class_cat', 'amr_code'])
    ordered_rows = [ab_code for ab_code in sorted_antibiotics['amr_code'] if ab_code in df_pivot.index]
    
    # Sort columns (organisms) by super-class, then class, then name
    organisms_df['class_id_cat'] = pd.Categorical(organisms_df['class_id'], categories=org_classes_df[org_classes_df.parent_id.notna()]['id'].tolist(), ordered=True)
    organisms_df['super_class_id'] = organisms_df['class_id'].map(org_classes_df.set_index('id')['parent_id'])
    organisms_df['super_class_id_cat'] = pd.Categorical(organisms_df['super_class_id'], categories=org_classes_df[org_classes_df.parent_id.isna()]['id'].tolist(), ordered=True)
    sorted_organisms = organisms_df.sort_values(by=['super_class_id_cat', 'class_id_cat', 'amr_code'])
    ordered_cols = [org_code for org_code in sorted_organisms['amr_code'] if org_code in df_pivot.columns]
    
    df_pivot = df_pivot.loc[ordered_rows, ordered_cols]

    for lang in LANGUAGES:
        html_content = generate_html(df_pivot, antibiotics_map, organisms_map, ab_classes_map, org_classes_map, language=lang)
        output_file = BASE_DIR / f"{OUTPUT_HTML_BASE_NAME}_{lang}.html"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"\nSuccessfully generated HTML report: {output_file.name}")

if __name__ == "__main__":
    main()
