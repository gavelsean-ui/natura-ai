from fpdf import FPDF
import os

class PDFReport(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 16)
        self.set_text_color(34, 139, 34) # Vert NATURA
        self.cell(0, 10, 'NATURA AI - Dossier Scientifique', 0, 1, 'C')
        self.set_font('Arial', 'I', 10)
        self.set_text_color(100, 100, 100)
        self.cell(0, 10, 'Rapport généré automatiquement - Analyse multi-sources', 0, 1, 'C')
        self.ln(5)
        self.set_draw_color(34, 139, 34)
        self.line(10, 30, 200, 30)
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(128)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

def generate_pdf(query, results):
    pdf = PDFReport()
    
    font_path = "C:/Windows/Fonts/arial.ttf"
    font_bold_path = "C:/Windows/Fonts/arialbd.ttf"
    
    if os.path.exists(font_path):
        pdf.add_font('Arial', '', font_path, uni=True)
        if os.path.exists(font_bold_path):
            pdf.add_font('Arial', 'B', font_bold_path, uni=True)
        else:
            pdf.add_font('Arial', 'B', font_path, uni=True)
    else:
        pdf.set_font('Helvetica', '', 10)

    pdf.add_page()
    pdf.set_font('Arial', '', 11)
    
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, f"Requête : {query}", 0, 1)
    pdf.set_font('Arial', '', 11)
    pdf.cell(0, 10, f"Nombre d'articles uniques : {len(results)}", 0, 1)
    pdf.ln(10)

    for idx, item in enumerate(results):
        pdf.set_font('Arial', 'B', 12)
        pdf.multi_cell(0, 8, f"[{item.get('score', 0)}/100] {item.get('title', 'Titre indisponible')}")
        pdf.ln(2)
        
        pdf.set_font('Arial', '', 10)
        sources = ', '.join(item.get('sources', []))
        pdf.cell(0, 6, f"Sources : {sources} | Date : {item.get('pub_date', 'N/A')}", 0, 1)
        pdf.cell(0, 6, f"Auteurs : {item.get('authors', 'N/A')}", 0, 1)
        pdf.cell(0, 6, f"Revue : {item.get('journal', 'N/A')} | DOI : {item.get('doi', 'N/A')}", 0, 1)
        if item.get('citations'):
            pdf.cell(0, 6, f"Citations : {item.get('citations')}", 0, 1)
        pdf.ln(3)

        ai_res = item.get('ai_analysis')
        if ai_res and "error" not in ai_res:
            pdf.set_font('Arial', 'B', 10)
            pdf.set_text_color(34, 139, 34)
            pdf.cell(0, 8, ">> Analyse de l'IA :", 0, 1)
            pdf.set_text_color(0, 0, 0)
            pdf.set_font('Arial', '', 10)
            
            plante = ai_res.get('plante', 'Non précisée')
            molecule = ai_res.get('molecule', 'Non précisée')
            patho = ai_res.get('pathologie', 'Non précisée')
            etude = ai_res.get('type_etude', 'Non précisé')
            res = ai_res.get('resultat', 'Non précisé')
            synthese = ai_res.get('resume_simple', '')
            
            pdf.cell(0, 6, f"Plante : {plante} | Molecule : {molecule}", 0, 1)
            pdf.cell(0, 6, f"Pathologie : {patho} | Type d'etude : {etude}", 0, 1)
            pdf.cell(0, 6, f"Resultat : {res}", 0, 1)
            pdf.multi_cell(0, 6, f"Synthèse : {synthese}")
            pdf.ln(5)

        pdf.set_font('Arial', 'B', 10)
        pdf.cell(0, 8, "Résumé original :", 0, 1)
        pdf.set_font('Arial', '', 9)
        
        abstract_clean = item.get('abstract', 'Aucun résumé').encode('latin-1', 'replace').decode('latin-1')
        pdf.multi_cell(0, 5, abstract_clean)
        
        pdf.ln(10)
        
        pdf.set_draw_color(200, 200, 200)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(10)

    # C'est ici qu'on a corrigé l'erreur : on renvoie directement les bytes
    return bytes(pdf.output())