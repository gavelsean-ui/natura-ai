import streamlit as st
from app.pubmed import search_pubmed
from app.storage import save_records, load_records, export_csv

st.set_page_config(page_title="NATURA AI", page_icon="🌿", layout="wide")
st.title("🌿 NATURA AI")
st.subheader("Prototype 0.1 — NATURA CONNECT")
st.write("Premier socle : recherche documentaire dans PubMed, dédoublonnage et mémoire locale des références.")

st.info(
    "Ce prototype organise des références scientifiques. Il ne valide pas une efficacité médicale, "
    "ne recommande aucun traitement et ne remplace pas l'expertise de chercheurs."
)

with st.form("search_form"):
    query = st.text_input("Recherche scientifique", placeholder='Ex. medicinal plants AND antiviral activity')
    max_results = st.selectbox("Nombre maximal de résultats", [5, 10, 20, 50], index=1)
    submitted = st.form_submit_button("Rechercher dans PubMed")

if submitted:
    if not query.strip():
        st.warning("Saisis un sujet de recherche.")
    else:
        with st.spinner("Interrogation de PubMed…"):
            try:
                records = search_pubmed(query.strip(), max_results)
                added = save_records(records)
                st.session_state["last_results"] = records
                st.success(f"{len(records)} référence(s) récupérée(s) ; {added} nouvelle(s) référence(s) ajoutée(s).")
            except Exception as exc:
                st.error(f"La recherche a échoué : {exc}")

results = st.session_state.get("last_results", [])
if results:
    st.markdown("### Résultats de la dernière recherche")
    for item in results:
        with st.expander(f"{item.get('title', 'Titre indisponible')} — PMID {item.get('pmid', '')}"):
            st.write("**Date :**", item.get("pub_date", "Non précisée"))
            st.write("**Auteurs :**", item.get("authors", "Non précisés"))
            st.write("**Revue :**", item.get("journal", "Non précisée"))
            st.write("**DOI :**", item.get("doi", "Non précisé"))
            st.write("**Résumé :**")
            st.write(item.get("abstract", "Aucun résumé disponible."))
            st.write("**Source :**", item.get("source_url", ""))

st.markdown("---")
st.markdown("### Mémoire documentaire locale")
saved = load_records()
st.write(f"Références uniques enregistrées : **{len(saved)}**")
if saved:
    st.download_button(
        "Télécharger les références en CSV",
        data=export_csv(saved),
        file_name="natura_ai_references.csv",
        mime="text/csv"
    )
    if st.checkbox("Afficher les références enregistrées"):
        for item in saved:
            st.write(f"- [{item.get('title', 'Sans titre')}]({item.get('source_url', '')}) — PMID {item.get('pmid', '')}")