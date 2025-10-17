import pandas as pd
import numpy as np
from pathlib import Path
import re
import json

def process_file(file_path, output_dir):
    df0 = pd.read_excel(file_path, header=None)
    date_str = str(df0.iloc[0, 0]) if not df0.empty else ""
    date_match = re.search(r'(\d{2})/(\d{2})/(\d{4})', date_str)
    date_formatted = f"{date_match.group(1)}/{date_match.group(2)}/{date_match.group(3)}" if date_match else "Unknown"

    df = pd.read_excel(file_path, header=1)
    df = df.loc[:, ~df.columns.isna()]
    df = df.loc[:, ~df.columns.astype(str).str.contains('^Unnamed')]
    df = df[~df['CountyName'].astype(str).str.contains('Total', case=False, na=False)]
    df['CountyName'] = df['CountyName'].astype(str).str.title()

    column_mapping = {
        'Dem': 'Democrat',
        'Rep': 'Republican',
        'No Aff': 'No Affiliation',
        'Total Count of All Voters': 'Total'
    }
    df = df.rename(columns=column_mapping)

    numeric_columns = ['Democrat', 'Republican', 'No Affiliation', 'Other', 'Total']
    for col in numeric_columns:
        if col in df.columns:
            df[col] = df[col].astype(str).str.replace(',', '').str.strip()
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)

    if 'CountyID' in df.columns:
        df['CountyID'] = pd.to_numeric(df['CountyID'], errors='coerce').fillna(0).astype(int)

    if 'Total' not in df.columns:
        parts = [c for c in ['Democrat', 'Republican', 'No Affiliation', 'Other'] if c in df.columns]
        df['Total'] = df[parts].sum(axis=1) if parts else 0

    share_cols = {}
    for party in ['Democrat', 'Republican', 'No Affiliation', 'Other']:
        if party in df.columns:
            share_col = f'{party} Share'
            share_vals = np.where(df['Total'] > 0, (df[party] / df['Total']) * 100, 0.0)
            share_cols[share_col] = np.round(share_vals, 2)

    for party in ['Democrat', 'Republican', 'No Affiliation', 'Other']:
        if party in df.columns and f'{party} Share' in share_cols:
            insert_loc = df.columns.get_loc(party) + 1
            df.insert(insert_loc, f'{party} Share', share_cols[f'{party} Share'])

    df = df.reset_index(drop=True)

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / "county.xlsx"
    df.to_excel(output_path, index=False)

    metadata = {
        "last_updated": date_formatted,
        "total_counties": int(len(df)),
        "file_name": "county.xlsx"
    }
    metadata_path = output_dir / "metadata.json"
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)

    print(f"Processed {file_path} -> {output_path}")
    print(f"Date extracted: {date_formatted}")
    print(f"Headers: {list(df.columns)}")
    print(f"Rows processed: {len(df)}")
    print(f"Metadata saved: {metadata_path}")

    return output_path
