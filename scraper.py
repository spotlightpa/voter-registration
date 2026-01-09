from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())
import requests
from pathlib import Path
from helpers import county, total, congress, house, senate
from helpers.upload_to_s3 import upload_to_s3

FILES_TO_DOWNLOAD = {
    "current_voter_stats.xls": "https://www.pa.gov/content/dam/copapwp-pagov/en/dos/resources/voting-and-elections/voting-and-election-statistics/currentvotestats.xls",
    "congress.xlsx": "https://www.pa.gov/content/dam/copapwp-pagov/en/dos/resources/voting-and-elections/voting-and-election-statistics/current%20voterregstatsbycongressionaldistricts.xls",
    "senate.xlsx": "https://www.pa.gov/content/dam/copapwp-pagov/en/dos/resources/voting-and-elections/voting-and-election-statistics/current%20voterregstatsbysenatorialdistricts.xls",
    "house.xlsx": "https://www.pa.gov/content/dam/copapwp-pagov/en/dos/resources/voting-and-elections/voting-and-election-statistics/current%20voterregstatsbylegislativedistricts.xls",
}

def download_files():
    data_dir = Path("data")
    raw_dir = data_dir / "raw"
    processed_dir = data_dir / "processed"

    raw_dir.mkdir(parents=True, exist_ok=True)
    processed_dir.mkdir(parents=True, exist_ok=True)

    for filename, url in FILES_TO_DOWNLOAD.items():
        resp = requests.get(url)
        resp.raise_for_status()
        raw_path = raw_dir / filename
        raw_path.write_bytes(resp.content)
        print(f"Downloaded: {raw_path}")

        if filename == "current_voter_stats.xls":
            processed_path = county.process_file(raw_path, processed_dir)
            total.process_file(processed_path, processed_dir)
        elif filename == "congress.xlsx":
            congress.process_file(raw_path, processed_dir)
        elif filename == "house.xlsx":
            house.process_file(raw_path, processed_dir)
        elif filename == "senate.xlsx":
            senate.process_file(raw_path, processed_dir)

    return list(data_dir.rglob("*"))

if __name__ == "__main__":
    download_files()
    urls = upload_to_s3()
    if not urls:
        print("No files uploaded.")