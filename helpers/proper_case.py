import pandas as pd
from pathlib import Path

def process_file(file_path, output_dir):
    df = pd.read_excel(file_path)
    
    first_column = df.columns[0]
    df[first_column] = df[first_column].astype(str).str.title()
    
    output_path = output_dir / file_path.name
    df.to_excel(output_path, index=False)
    
    print(f"Processed {file_path} -> {output_path}")
    return output_path