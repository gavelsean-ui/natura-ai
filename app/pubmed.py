import time
import xml.etree.ElementTree as ET
import requests

BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
HEADERS = {"User-Agent": "NATURA-AI-prototype/0.4"}
TOOL_PARAMS = {"tool": "natura_ai"}

def _text(node, path):
    if node is None: return ""
    found = node.find(path)
    return "".join(found.itertext()).strip() if found is not None else ""

def _extract_doi(article):
    for aid in article.findall(".//ArticleIdList/ArticleId"):
        if (aid.attrib.get("IdType") or "").lower() == "doi" and aid.text:
            return aid.text.strip()
    for eloc in article.findall(".//ELocationID"):
        if (eloc.attrib.get("EIdType") or "").lower() == "doi" and eloc.text:
            return eloc.text.strip()
    return ""

def search_pubmed(query: str, limit: int = 10):
    if not query: return []
    res = requests.get(BASE + "esearch.fcgi", params={"db": "pubmed", "term": query, "retmax": limit, "retmode": "json", "sort": "relevance", **TOOL_PARAMS}, headers=HEADERS, timeout=30)
    res.raise_for_status()
    ids = res.json().get("esearchresult", {}).get("idlist", [])
    if not ids: return []
    
    time.sleep(0.34)
    detail = requests.get(BASE + "efetch.fcgi", params={"db": "pubmed", "id": ",".join(ids), "retmode": "xml", **TOOL_PARAMS}, headers=HEADERS, timeout=45)
    detail.raise_for_status()
    
    try: root = ET.fromstring(detail.text)
    except ET.ParseError: return []

    records = []
    for article in root.findall(".//PubmedArticle"):
        medline = article.find("MedlineCitation")
        art = medline.find("Article") if medline is not None else None
        pmid = _text(medline, "PMID")
        title = _text(art, "ArticleTitle")
        
        abstract_parts = []
        if art is not None:
            for part in art.findall(".//Abstract/AbstractText"):
                label = part.attrib.get("Label")
                text = "".join(part.itertext()).strip()
                if text: abstract_parts.append(f"{label}: {text}" if label else text)

        authors = []
        if art is not None:
            for author in art.findall(".//AuthorList/Author"):
                coll = _text(author, "CollectiveName")
                if coll: authors.append(coll)
                else:
                    name = " ".join(x for x in [_text(author, "ForeName"), _text(author, "LastName")] if x)
                    if name: authors.append(name)

        journal = _text(art, "Journal/Title")
        pub_date = _text(art, "Journal/JournalIssue/PubDate/Year") or _text(art, "Journal/JournalIssue/PubDate/MedlineDate")
        
        records.append({
            "pmid": pmid,
            "title": title or "Titre indisponible",
            "authors": "; ".join(authors) if authors else "Non précisés",
            "journal": journal or "Non précisée",
            "pub_date": pub_date or "Non précisée",
            "doi": _extract_doi(article) or "Non précisé",
            "abstract": "\n".join(abstract_parts) or "Aucun résumé disponible.",
            "source": "PubMed",
            "type": _text(art, "PublicationTypeList/PublicationType") or "Journal Article",
            "source_url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/" if pmid else "",
        })
    return records