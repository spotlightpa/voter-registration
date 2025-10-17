import pandas as pd
from pathlib import Path
import json
from datetime import datetime

def process_file(file_path, output_dir):
    file_path = Path(file_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    df = pd.read_excel(file_path)

    party_order = ['Democrat', 'Republican', 'No Affiliation', 'Other', 'Total']
    present = [c for c in party_order if c in df.columns]

    totals_by_party = {c: int(df[c].sum()) for c in present}

    summary_df = pd.DataFrame({
        "Party": present,
        "Total": [totals_by_party[c] for c in present],
    })
    totals_path = output_dir / "total.xlsx"
    summary_df.to_excel(totals_path, index=False)
    print(f"Created totals summary -> {totals_path}")

    metadata_path = output_dir / "metadata.json"
    existing = {}
    if metadata_path.exists():
        try:
            existing = json.loads(metadata_path.read_text())
        except Exception:
            existing = {}

    source_date = existing.get("last_updated", "Unknown")
    generated_at = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

    top_level = {
        "last_updated": source_date,
        "generated_at_utc": generated_at,
        "file_name": existing.get("file_name", file_path.name),
        "total_counties": int(existing.get("total_counties", len(df)))
    }

    consolidated = {
        **top_level,
        "artifacts": {
            "county": {
                "file_name": file_path.name,
                "total_counties": int(len(df)),
                "rows_in_source": int(len(df)),
                "source_date": source_date
            },
            "totals": {
                "file_name": totals_path.name,
                "parties_included": present,
                "totals_by_party": totals_by_party,
                "source_date": source_date
            }
        }
    }

    metadata_path.write_text(json.dumps(consolidated, indent=2))
    print(f"Updated consolidated metadata -> {metadata_path}")

    old_totals_meta = output_dir / "total_metadata.json"
    if old_totals_meta.exists():
        old_totals_meta.unlink()
        print("Removed legacy file -> total_metadata.json")

    return totals_path
