import pandas as pd
import numpy as np
from pathlib import Path
import re
import json

def process_file(file_path, output_dir):
    df = pd.read_excel(file_path, header=0)
    
    df = df.loc[:, ~df.columns.astype(str).str.contains('^Unnamed')]
    
    df['DistrictCode'] = df['DistrictCode'].ffill()
    
    df = df[df['CountyName'].astype(str).str.contains('Sub Total', case=False, na=False)]
    
    df = df.drop(columns=['CountyName'])
    
    df['DistrictCode'] = pd.to_numeric(df['DistrictCode'], errors='coerce').fillna(0).astype(int)

    numeric_columns = ['Democratic', 'Republican', 'Libertarian', 'Green', 'No Affiliation', 'Other', 'Total']
    for col in numeric_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
    
    df = df.sort_values('DistrictCode').reset_index(drop=True)
    
    column_order = ['DistrictCode', 'Democratic', 'Republican', 'Libertarian', 'Green', 'No Affiliation', 'Other', 'Total']
    df = df[[col for col in column_order if col in df.columns]]
    
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_path = output_dir / "congress.xlsx"
    df.to_excel(output_path, index=False)
    
    print(f"Processed {file_path} -> {output_path}")
    print(f"Districts processed: {len(df)}")
    print(f"Headers: {list(df.columns)}")
    print(f"\nFirst few rows:")
    print(df.head())
    
    return output_path