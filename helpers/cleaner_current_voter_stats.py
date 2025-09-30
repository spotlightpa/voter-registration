import pandas as pd
from pathlib import Path
import re

def process_file(file_path, output_dir):
    df = pd.read_excel(file_path, header=None)
    
    date_str = str(df.iloc[0, 0]) if not df.empty else ""
    date_match = re.search(r'(\d{2})/(\d{2})/(\d{4})', date_str)
    
    if date_match:
        month, day, year = date_match.groups()
        date_suffix = f"{year}_{month}_{day}"
    else:
        date_suffix = "unknown_date"
    
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
    
    df = df.reset_index(drop=True)

    original_name = file_path.stem
    extension = file_path.suffix
    new_filename = f"{original_name}_{date_suffix}{extension}"
    output_path = output_dir / new_filename
    
    df.to_excel(output_path, index=False)
    
    print(f"Processed {file_path} -> {output_path}")
    print(f"Date extracted: {date_suffix}")
    print(f"Headers: {list(df.columns)}")
    print(f"Rows processed: {len(df)}")
    
    return output_path