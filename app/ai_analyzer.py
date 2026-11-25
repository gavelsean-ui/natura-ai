import json
import anthropic

def analyze_abstract_with_ai(api_key, abstract_text):
    if not api_key or not abstract_text or "Aucun résumé" in abstract_text:
        return None

    try:
        # On retire le /v1 final, car la librairie l'ajoute toute seule
        client = anthropic.Anthropic(
            base_url="https://apihub.agnes-ai.com",
            api_key=api_key
        )
        
        prompt = f"""
        Tu es un expert en pharmacognosie et en évaluation scientifique.
        Analyse le résumé d'article scientifique suivant et extrais les informations clés.
        Renvoie UNIQUEMENT un objet JSON valide avec les clés suivantes (en français) :
        - "plante" : Le nom de la plante principale (ou "" si non mentionnée)
        - "molecule" : La molécule active (ou "" si non mentionnée)
        - "pathologie" : La maladie ou condition ciblée (ou "" si non mentionnée)
        - "type_etude" : Le type d'étude (ex: "Essai clinique", "In vitro", "Etude animale", "Revue")
        - "resultat" : "Positif", "Négatif", "Mitigé" ou "Non applicable"
        - "resume_simple" : Une phrase de synthèse en français expliquant la conclusion.

        Résumé de l'article :
        "{abstract_text}"
        """
        
        message = client.messages.create(
            model="agnes-3.0-flash",
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}]
        )
        
        text = message.content[0].text.strip()
        
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
            
        return json.loads(text.strip())
    except Exception as e:
        return {"error": str(e)}