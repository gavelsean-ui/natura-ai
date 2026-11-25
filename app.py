import streamlit as st
from app.pubmed import search_pubmed
from app.europe_pmc import search_europe_pmc
from app.crossref import search_crossref, get_citations_from_doi
from app.dedup import deduplicate_records
from app.storage import save_records, load_records, export_csv
from app.score import calculate_natura_score
from app.ai_analyzer import analyze_abstract_with_ai
from app.pdf_generator import generate_pdf

st.set_page_config(page_title="NATURA AI", page_icon="🌿", layout="wide")
st.title("🌿 NATURA AI")
st.subheader("Prototype 0.9 — Rapports PDF")
st.write("Recherche multi-sources, enrichissement et génération de rapports PDF professionnels.")

# --- BARRE LATÉRALE POUR LA CLÉ API ---
api_key = st.secrets.get("AGNES_API_KEY", "")
if not api_key:
    with st.sidebar:
        st.header("🔑 Configuration IA")
        api_key = st.text_input("Clé API Agnes AI", type="password", help="Obtenez une clé sur agnes-ai.com")
        st.caption("L'IA analysera les résumés pour enrichir le rapport final.")

st.info(
    "Le NATURA SCORE évalue la solidité méthodologique et l'impact d'un article basé sur ses métadonnées. "
    "Il ne valide pas une efficacité médicale et ne remplace pas la lecture critique."
)

with st.form("search_form"):
    query = st.text_input(
        "Recherche scientifique (en anglais ou nom scientifique recommandé)", 
        placeholder='Ex. "Syzygium aromaticum"'
    )
    
    col1, col2 = st.columns(2)
    with col1:
        max_results = st.selectbox("Nombre maximal de résultats par base", [5, 10, 20], index=1)
    with col2:
        source_choice = st.selectbox("Base de données", ["Les 3 bases (recommandé)", "PubMed", "Europe PMC", "Crossref"])
        
    submitted = st.form_submit_button("Rechercher")

if submitted:
    if not query.strip():
        st.warning("Saisis un sujet de recherche.")
    else:
        with st.spinner("Interrogation des bases de données…"):
            all_records = []
            errors = []

            if source_choice in ["Les 3 bases (recommandé)", "PubMed"]:
                try: all_records.extend(search_pubmed(query.strip(), max_results))
                except Exception as e: errors.append(f"PubMed a échoué : {e}")

            if source_choice in ["Les 3 bases (recommandé)", "Europe PMC"]:
                try: all_records.extend(search_europe_pmc(query.strip(), max_results))
                except Exception as e: errors.append(f"Europe PMC a échoué : {e}")

            if source_choice in ["Les 3 bases (recommandé)", "Crossref"]:
                try: all_records.extend(search_crossref(query.strip(), max_results))
                except Exception as e: errors.append(f"Crossref a échoué : {e}")

            for err in errors:
                st.warning(err)

            if not all_records and errors:
                st.error("La recherche a complètement échoué.")
            else:
                with st.spinner("Récupération du nombre de citations via Crossref…"):
                    for r in all_records:
                        if not r.get("citations") and r.get("doi") and r.get("doi") != "Non précisé":
                            cites = get_citations_from_doi(r["doi"])
                            if cites > 0:
                                r["citations"] = cites

                if source_choice == "Les 3 bases (recommandé)":
                    final_records = deduplicate_records(all_records)
                else:
                    final_records = all_records
                    for r in final_records:
                        r["sources"] = [r["source"]]

                for r in final_records:
                    score, _ = calculate_natura_score(r)
                    r["score"] = score

                final_records.sort(key=lambda x: x.get("score", 0), reverse=True)

                added = save_records(final_records)
                st.session_state["last_results"] = final_records
                st.session_state["last_query"] = query.strip()
                
                st.success(f"{len(final_records)} référence(s) unique(s) trouvée(s). {added} nouvelle(s) ajoutée(s).")

results = st.session_state.get("last_results", [])
if results:
    st.markdown("### Résultats de la dernière recherche")
    
    # --- BOUTON PDF ---
    if st.button("📄 Générer le rapport PDF professionnel"):
        if not api_key:
            st.warning("⚠️ Sans clé API, le rapport contiendra uniquement les résumés bruts.")
            
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for i, item in enumerate(results):
            status_text.text(f"Analyse de l'article {i+1}/{len(results)} avec l'IA...")
            if api_key and item.get("abstract"):
                ai_res = analyze_abstract_with_ai(api_key, item.get("abstract", ""))
                item["ai_analysis"] = ai_res
            progress_bar.progress((i + 1) / len(results))
            
        status_text.text("Génération du document PDF...")
        
        pdf_bytes = generate_pdf(st.session_state.get('last_query', ''), results)
        
        status_text.text("✅ Rapport PDF prêt !")
        
        query_safe = "".join(c for c in st.session_state.get('last_query', 'recherche') if c.isalnum() or c in (' ', '_')).replace(' ', '_')
        
        st.download_button(
            label="⬇️ Télécharger le dossier PDF",
            data=pdf_bytes,
            file_name=f"natura_dossier_{query_safe}.pdf",
            mime="application/pdf",
            use_container_width=True
        )
    # ------------------------------------------------

    for idx, item in enumerate(results):
        sources_str = ", ".join(item.get("sources", ["Inconnue"]))
        score = item.get("score", 0)
        score_badge = f"🟢 {score}/100" if score >= 70 else (f"🟠 {score}/100" if score >= 40 else f"🔴 {score}/100")
        
        with st.expander(f"{score_badge} | {item.get('title', 'Titre indisponible')} [{sources_str}]"):
            st.write("**Auteurs :**", item.get("authors", "Non précisés"))
            st.write("**Revue :**", item.get("journal", "Non précisée"))
            st.write("**Résumé :**")
            st.write(item.get("abstract", "Aucun résumé disponible."))
            
            st.markdown("---")
            if st.button(f"🧠 Analyser avec l'IA", key=f"ai_btn_{idx}"):
                if not api_key:
                    st.warning("Veuillez entrer votre clé API Agnes AI dans la barre latérale gauche.")
                else:
                    with st.spinner("L'IA lit l'article..."):
                        ai_result = analyze_abstract_with_ai(api_key, item.get("abstract", ""))
                        if ai_result and "error" not in ai_result:
                            st.success("Analyse terminée !")
                            st.markdown(f"**🌿 Plante :** {ai_result.get('plante', 'Non précisée')}")
                            st.markdown(f"**🧪 Molécule :** {ai_result.get('molecule', 'Non précisée')}")
                            st.markdown(f"**🤒 Pathologie :** {ai_result.get('pathologie', 'Non précisée')}")
                            st.markdown(f"**🔬 Type d'étude :** {ai_result.get('type_etude', 'Non précisé')}")
                            st.markdown(f"**📊 Résultat :** {ai_result.get('resultat', 'Non précisé')}")
                            st.markdown(f"**📝 Synthèse :** *{ai_result.get('resume_simple', '')}*")
                        elif ai_result and "error" in ai_result:
                            st.error(f"Erreur de l'IA : {ai_result['error']}")
