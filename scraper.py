import requests
from pathlib import Path
from helpers import cleaner_current_voter_stats

FILES_TO_DOWNLOAD = {
    "current_voter_stats.xls": "https://www.pa.gov/content/dam/copapwp-pagov/en/dos/resources/voting-and-elections/voting-and-election-statistics/currentvotestats.xls",
}

FILE_HELPERS = {
    "current_voter_stats.xls": cleaner_current_voter_stats.process_file,
}

def download_files():
    data_dir = Path("data")
    raw_dir = data_dir / "raw"
    processed_dir = data_dir / "processed"
    
    raw_dir.mkdir(parents=True, exist_ok=True)
    processed_dir.mkdir(parents=True, exist_ok=True)
    
    for filename, url in FILES_TO_DOWNLOAD.items():
        response = requests.get(url)
        response.raise_for_status()
        
        file_path = raw_dir / filename
        with open(file_path, 'wb') as f:
            f.write(response.content)
        
        print(f"Downloaded: {file_path}")
        
        if filename in FILE_HELPERS:
            FILE_HELPERS[filename](file_path, processed_dir)
    
    return list(data_dir.rglob("*"))

if __name__ == "__main__":
    download_files()