import requests

BASE = "https://api.crossref.org/works"

def search_crossref(query: str, limit: int = 10):
    if not query: return []
    
    params = {
        "query": query,
        "rows": limit,
        "select": "DOI,title,author,published-print,publisher,is-referenced-by-count,type"
    }
    headers = {"User-Agent": "NATURA-AI/0.5 (mailto:votre_email@exemple.com)"}
    
    try:
        res = requests.get(BASE, params=params, headers=headers, timeout=60)
        res.raise_for_status()
        items = res.json().get("message", {}).get("items", [])
    except Exception:
        return []

    records = []
    for item in items:
        doi = item.get("DOI", "")
        if not doi: continue
        title_list = item.get("title", [])
        title = title_list[0] if title_list else "Titre indisponible"
        
        authors = []
        for auth in item.get("author", []):
            name = f"{auth.get('given', '')} {auth.get('family', '')}".strip()
            if name: authors.append(name)

        pub_date = ""
        if "published-print" in item:
            parts = item["published-print"].get("date-parts", [[]])[0]
            if parts: pub_date = str(parts[0])

        records.append({
            "pmid": "",
            "doi": doi.lower(),
            "title": title,
            "authors": "; ".join(authors) if authors else "Non précisés",
            "journal": item.get("publisher", "Éditeur inconnu"),
            "pub_date": pub_date or "Non précisée",
            "abstract": "Résumé non disponible dans Crossref.",
            "source": "Crossref",
            "source_url": f"https://doi.org/{doi}",
            "citations": item.get("is-referenced-by-count", 0),
            "type": item.get("type", "Inconnu")
        })
    return records

def get_citations_from_doi(doi: str):
    """Récupère uniquement le nombre de citations pour un DOI donné."""
    if not doi or doi == "Non précisé": return 0
    url = f"{BASE}/{doi}"
    try:
        res = requests.get(url, timeout=10)
        if res.status_code == 200:
            return res.json().get("message", {}).get("is-referenced-by-count", 0)
    except Exception:
        pass
    return 0