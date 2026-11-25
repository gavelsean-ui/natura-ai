import csv, io, json
from pathlib import Path
from app.dedup import normalize_title

DATA_DIR = Path("data")
DB_FILE = DATA_DIR / "references.json"
CSV_FIELDS = ["pmid", "doi", "title", "authors", "journal", "pub_date", "abstract", "sources", "source_url"]

def load_records():
    if not DB_FILE.exists(): return []
    try: 
        data = json.loads(DB_FILE.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except Exception: return []

def _get_key(item):
    if item.get("pmid"): return f"pmid:{item['pmid']}"
    if item.get("doi"): return f"doi:{item['doi'].lower()}"
    return f"title:{normalize_title(item.get('title', ''))}"

def save_records(records):
    if not isinstance(records, list): return 0
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    existing = load_records()
    known = {_get_key(item) for item in existing}
    
    added = 0
    for item in records:
        key = _get_key(item)
        if not key or key in known: continue
        # Si 'source' existe mais pas 'sources', on harmonise
        if "source" in item and "sources" not in item:
            item["sources"] = [item["source"]]
        existing.append(item)
        known.add(key)
        added += 1
        
    DB_FILE.write_text(json.dumps(existing, ensure_ascii=False, indent=2), encoding="utf-8")
    return added

def export_csv(records):
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=CSV_FIELDS, extrasaction="ignore")
    writer.writeheader()
    for item in (records or []):
        row = item.copy()
        # Transforme la liste ['PubMed', 'Europe PMC'] en texte "PubMed, Europe PMC"
        if isinstance(row.get("sources"), list):
            row["sources"] = ", ".join(row["sources"])
        writer.writerow({key: row.get(key, "") for key in CSV_FIELDS})
    return output.getvalue().encode("utf-8-sig")