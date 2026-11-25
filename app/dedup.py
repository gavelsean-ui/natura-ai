import unicodedata
import re

def normalize_title(title):
    if not title: return ""
    title = unicodedata.normalize('NFKD', title).encode('ASCII', 'ignore').decode('utf-8')
    return re.sub(r'[^a-z0-9]', '', title.lower())

def deduplicate_records(records):
    unique = []
    seen_pmids = set()
    seen_dois = set()
    seen_titles = set()

    for r in records:
        pmid = str(r.get("pmid", "")).strip()
        doi = str(r.get("doi", "")).strip().lower()
        norm_title = normalize_title(r.get("title"))

        existing_item = None
        if pmid and pmid in seen_pmids:
            existing_item = next((x for x in unique if str(x.get("pmid")) == pmid), None)
        elif doi and doi in seen_dois:
            existing_item = next((x for x in unique if str(x.get("doi")).lower() == doi), None)
        elif norm_title and norm_title in seen_titles:
            existing_item = next((x for x in unique if normalize_title(x.get("title")) == norm_title), None)

        if existing_item:
            new_source = r.get("source", "Inconnue")
            if new_source not in existing_item["sources"]:
                existing_item["sources"].append(new_source)
            
            if r.get("citations") and not existing_item.get("citations"):
                existing_item["citations"] = r["citations"]
            
            # Si l'ancien a un type faible ("journal article") et le nouveau un type fort ("clinical trial")
            if r.get("type") and existing_item.get("type"):
                old_t = str(existing_item["type"]).lower()
                new_t = str(r["type"]).lower()
                if ("clinical trial" in new_t or "review" in new_t) and ("journal article" in old_t):
                    existing_item["type"] = r["type"]

            if r.get("abstract") and "Aucun résumé" in existing_item.get("abstract", "") and "Aucun résumé" not in r["abstract"]:
                existing_item["abstract"] = r["abstract"]
        else:
            r["sources"] = [r.get("source", "Inconnue")]
            unique.append(r)
            if pmid: seen_pmids.add(pmid)
            if doi: seen_dois.add(doi)
            if norm_title: seen_titles.add(norm_title)

    return unique