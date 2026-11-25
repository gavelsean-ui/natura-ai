def calculate_natura_score(record):
    score = 0
    details = []

    # 1. Type d'étude (jusqu'à 40 points)
    ptype = str(record.get("type", "")).lower()
    if "clinical trial" in ptype or "randomized" in ptype:
        score += 40
        details.append("Type : Essai clinique (+40)")
    elif "systematic review" in ptype or "meta-analysis" in ptype:
        score += 30
        details.append("Type : Revue systématique/Méta-analyse (+30)")
    elif "review" in ptype:
        score += 15
        details.append("Type : Revue de littérature (+15)")
    elif "preprint" in ptype:
        score += 0
        details.append("Type : Preprint (non évalué par les pairs) (+0)")
    else:
        score += 10
        details.append("Type : Article standard (+10)")

    # 2. Citations (jusqu'à 30 points)
    citations = int(record.get("citations", 0) or 0)
    if citations >= 100:
        score += 30
        details.append(f"Citations : {citations} (+30)")
    elif citations >= 20:
        score += 20
        details.append(f"Citations : {citations} (+20)")
    elif citations >= 5:
        score += 10
        details.append(f"Citations : {citations} (+10)")
    else:
        details.append(f"Citations : {citations} (+0)")

    # 3. Complétude des données (jusqu'à 30 points)
    if record.get("doi") and record.get("doi") != "Non précisé":
        score += 15
        details.append("DOI présent (+15)")
    if record.get("abstract") and "Aucun résumé" not in record.get("abstract") and "non disponible" not in record.get("abstract"):
        score += 15
        details.append("Résumé présent (+15)")

    # On plafonne à 100
    final_score = min(score, 100)
    return final_score, details