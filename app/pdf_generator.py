from fpdf import FPDF
import os

class PDFReport(FPDF):
    def header(self):
        self.set_font('Helvetica', 'B', 16)
        self.set_text_color(34, 139, 34)
        self.cell(0, 10, 'NATURA AI - Dossier Scientifique', 0, 1, 'C')
        self.set_font('Helvetica', 'I', 10)
        self.set_text_color(100, 100, 100)
        self.cell(0, 10, 'Rapport genere automatiquement - Analyse multi-sources', 0, 1, 'C')
        self.ln(5)
        self.set_draw_color(34, 139, 34)
        self.line(10, 30, 200, 30)
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(128)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

def sanitize_text(text):
    """Nettoie le texte pour éviter les crashs d'encodage"""
    if not isinstance(text, str):
        text = str(text)
    return text.encode('latin-1', 'replace').decode('latin-1')

def generate_pdf(query, results):
    pdf = PDFReport()
    pdf.set_font('Helvetica', '', 10)

    pdf.add_page()
    
    # Infos générales
    pdf.set_font('Helvetica', 'B', 12)
    pdf.cell(0, 10, sanitize_text(f"Requete : {query}"), 0, 1)
    pdf.set_font('Helvetica', '', 11)
    pdf.cell(0, 10, f"Nombre d'articles uniques : {len(results)}", 0, 1)
    pdf.ln(10)

    for idx, item in enumerate(results):
        # Titre
        pdf.set_font('Helvetica', 'B', 12)
        title = sanitize_text(f"[{item.get('score', 0)}/100] {item.get('title', 'Titre indisponible')}")
        pdf.multi_cell(0, 8, title)
        pdf.ln(2)
        
        # Métadonnées
        pdf.set_font('Helvetica', '', 10)
        sources = sanitize_text(', '.join(item.get('sources', [])))
        authors = sanitize_text(item.get('authors', 'N/A'))
        journal = sanitize_text(item.get('journal', 'N/A'))
        doi = sanitize_text(item.get('doi', 'N/A'))
        
        pdf.cell(0, 6, f"Sources : {sources} | Date : {item.get('pub_date', 'N/A')}", 0, 1)
        pdf.cell(0, 6, f"Auteurs : {authors}", 0, 1)
        pdf.cell(0, 6, f"Revue : {journal} | DOI : {doi}", 0, 1)
        if item.get('citations'):
            pdf.cell(0, 6, f"Citations : {item.get('citations')}", 0, 1)
        pdf.ln(3)

        # Analyse IA
        ai_res = item.get('ai_analysis')
        if ai_res and "error" not in ai_res:
            pdf.set_font('Helvetica', 'B', 10)
            pdf.set_text_color(34, 139, 34)
            pdf.cell(0, 8, ">> Analyse de l'IA :", 0, 1)
            pdf.set_text_color(0, 0, 0)
            pdf.set_font('Helvetica', '', 10)
            
            plante = sanitize_text(ai_res.get('plante', 'Non precisee'))
            molecule = sanitize_text(ai_res.get('molecule', 'Non precisee'))
            patho = sanitize_text(ai_res.get('pathologie', 'Non precisee'))
            etude = sanitize_text(ai_res.get('type_etude', 'Non precise'))
            res = sanitize_text(ai_res.get('resultat', 'Non precise'))
            synthese = sanitize_text(ai_res.get('resume_simple', ''))
            
            pdf.cell(0, 6, f"Plante : {plante} | Molecule : {molecule}", 0, 1)
            pdf.cell(0, 6, f"Pathologie : {patho} | Type d'etude : {etude}", 0, 1)
            pdf.cell(0, 6, f"Resultat : {res}", 0, 1)
            pdf.multi_cell(0, 6, f"Synthese : {synthese}")
            pdf.ln(5)

        # Résumé
        pdf.set_font('Helvetica', 'B', 10)
        pdf.cell(0, 8, "Resume original :", 0, 1)
        pdf.set_font('Helvetica', '', 9)
        
        abstract_clean = sanitize_text(item.get('abstract', 'Aucun resume'))
        pdf.multi_cell(0, 5, abstract_clean)
        
        pdf.ln(10)
        pdf.set_draw_color(200, 200, 200)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(10)

    return bytes(pdf.output())
