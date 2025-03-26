import streamlit as st
import pandas as pd
import numpy as np
from st_aggrid import AgGrid
from st_aggrid.grid_options_builder import GridOptionsBuilder

st.title("Calcul des articles par fourchette de taille")

st.write("""
Cette application vous permet de copier-coller un jeu de données au format [nombre] \ttaille\t[fourchette de taille] ou [nombre] \ttaille\t[taille1/taille2].
Le tableau se remplira automatiquement et les totaux par fourchette de taille seront calculés.
""")

# Fonction pour parser les données collées en évitant la perte de quantité
def parse_text_data(text):
    lines = text.strip().split('\n')
    data = []
    for line in lines:
        parts = [p.strip() for p in line.split('\t') if p.strip()]
        if len(parts) == 3 and parts[1].lower() == 'taille':
            try:
                qty = int(parts[0])
                tailles = parts[2].split('/')  # Gérer les tailles multiples comme "38/40"
                nb_tailles = len(tailles)
                base_qty = qty // nb_tailles  # Répartition de base
                remainder = qty % nb_tailles  # Reste à répartir
                
                for i, taille in enumerate(tailles):
                    taille = int(taille)
                    if 34 <= taille <= 64 and taille % 2 == 0:
                        adjusted_qty = base_qty + (1 if i < remainder else 0)  # Répartir le reste équitablement
                        data.append({"Quantité": adjusted_qty, "taille": "taille", "Fourchette de taille": taille})
            except ValueError:
                continue
    return pd.DataFrame(data)

# Initialiser text_data dans la session si nécessaire
if 'text_data' not in st.session_state:
    st.session_state.text_data = ''

# Boutons pour analyser et effacer les données
col1, col2 = st.columns(2)

with col1:
    if st.button("Analyser les données"):
        if st.session_state.text_data.strip():
            parsed_data = parse_text_data(st.session_state.text_data)
            if not parsed_data.empty:
                st.session_state.table_data = parsed_data
            else:
                st.warning("Aucune donnée valide n'a été trouvée. Veuillez vérifier votre saisie.")

with col2:
    if st.button("Effacer les données"):
        st.session_state.text_data = ""  # Réinitialise le contenu du text_area
        if 'table_data' in st.session_state:
            del st.session_state.table_data

# Champ de texte pour coller les données
text_data = st.text_area(
    "Collez vos données ici (format: nombre\ttaille\tfourchette de taille ou nombre\ttaille\ttaille1/taille2)",
    value=st.session_state.text_data,
    key="unique_data_input",  # Clé unique ajoutée
    height=200,
    placeholder="8\ttaille\t36\n14\ttaille\t38/40\n31\ttaille\t42/44\n..."
)

# Mettre à jour la valeur de session
st.session_state.text_data = text_data

# Fonction pour calculer les totaux par fourchette de taille
def calculate_totals(data):
    tailles = {
        "34-48": 0,  # 34/36/38/40/42/44/46/48
        "50-52": 0,
        "54-56": 0,
        "58-60": 0,
        "62-64": 0
    }
    
    for _, row in data.iterrows():
        try:
            quantite = int(row["Quantité"])
            taille = int(row["Fourchette de taille"])
            if 34 <= taille <= 48:
                tailles["34-48"] += quantite
            elif 50 <= taille <= 52:
                tailles["50-52"] += quantite
            elif 54 <= taille <= 56:
                tailles["54-56"] += quantite
            elif 58 <= taille <= 60:
                tailles["58-60"] += quantite
            elif 62 <= taille <= 64:
                tailles["62-64"] += quantite
        except ValueError:
            continue
    return tailles

# Calcul des résultats si des données existent
if 'table_data' in st.session_state and not st.session_state.table_data.empty:
    totals = calculate_totals(st.session_state.table_data)
    total_articles = sum(totals.values())
    
    st.markdown("## 📊 Résultats de l'analyse")
    
    styled_results = pd.DataFrame({
        "Fourchette de tailles": list(totals.keys()),
        "Nombre d'articles": list(totals.values())
    })
    
    styled_results.loc[len(styled_results)] = ["Total", total_articles]
    
    st.dataframe(styled_results)
    
    # Option pour télécharger les résultats
    csv = styled_results.to_csv(index=False)
    st.download_button(
        label="📥 Télécharger les résultats (CSV)",
        data=csv,
        file_name='resultats_analyse_tailles.csv',
        mime='text/csv',
    )