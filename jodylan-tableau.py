import streamlit as st
import pandas as pd
import re
import pyexcel as p

# Définition des catégories de tailles
size_categories = {
    "34/36 et 46/48": [34, 36, 46, 48],
    "38/40 et 42/44": [38, 40, 42, 44],
    "50/52": [50, 52],
    "54/56": [54, 56],
    "58/60": [58, 60],
    "62/64": [62, 64],
}

def extract_quantity_and_size(df):
    """
    Détecte la colonne contenant "taille" avec un nombre avant et après.
    Corrige l'erreur qui omet des lignes au début du tableau.
    """
    for col in df.columns:
        for idx, value in enumerate(df[col]):
            if isinstance(value, str) and "taille" in value.lower():
                try:
                    prev_value = df.iloc[idx, col - 1]
                    next_value = df.iloc[idx, col + 1]
                    if str(prev_value).isdigit() and str(next_value).isdigit():
                        return df.iloc[idx :, col - 1 : col + 2].dropna()  # Prendre toutes les lignes en dessous
                except (IndexError, ValueError):
                    continue
    return None

def process_excel(file):
    """Traite un fichier Excel et regroupe les quantités par fourchette de tailles."""
    df = pd.read_excel(file, engine="openpyxl")
    
    size_totals = {key: 0 for key in size_categories}
    extracted_data = extract_quantity_and_size(df)
    
    if extracted_data is None:
        return "Erreur : Impossible de localiser les colonnes à analyser."

    st.write("🔍 **Vérification des données extraites :**", extracted_data)  # Debugging

    for _, row in extracted_data.iterrows():
        try:
            quantity, taille_txt, taille_num = int(row.iloc[0]), str(row.iloc[1]), int(row.iloc[2])
            if "taille" in taille_txt.lower():
                for category, sizes in size_categories.items():
                    if taille_num in sizes:
                        size_totals[category] += quantity
                        break
        except (ValueError, IndexError):
            continue

    total_articles = sum(size_totals.values())
    result_df = pd.DataFrame(list(size_totals.items()), columns=["Fourchette de tailles", "Nombre total de pièces"])
    result_df.loc[len(result_df)] = ["Total d'articles", total_articles]
    
    return result_df

def process_ods(file):
    """Traite un fichier ODS et détecte dynamiquement les bonnes colonnes."""
    data = p.get_book_dict(file_type="ods", file_content=file.read())

    # 🔍 1️⃣ Vérifier si "BL" existe, sinon choisir l'onglet avec le plus de données
    sheet_name = "BL" if "BL" in data else max(data, key=lambda k: len(data[k]))

    df = pd.DataFrame(data[sheet_name])

    # 🔍 2️⃣ Identifier la colonne contenant "taille" et les valeurs associées
    extracted_data = extract_quantity_and_size(df)
    if extracted_data is None:
        return "Erreur : Impossible de localiser les colonnes à analyser."

    st.write("🔍 **Vérification des données extraites (ODS) :**", extracted_data)  # Debugging

    size_totals = {key: 0 for key in size_categories}

    for _, row in extracted_data.iterrows():
        try:
            quantity, taille_txt, taille_num = int(row.iloc[0]), str(row.iloc[1]), int(row.iloc[2])
            if "taille" in taille_txt.lower():
                for category, sizes in size_categories.items():
                    if taille_num in sizes:
                        size_totals[category] += quantity
                        break
        except (ValueError, IndexError):
            continue

    total_articles = sum(size_totals.values())
    result_df = pd.DataFrame(list(size_totals.items()), columns=["Fourchette de tailles", "Nombre total de pièces"])
    result_df.loc[len(result_df)] = ["Total d'articles", total_articles]
    
    return result_df

def main():
    st.title("Analyse automatique des bordereaux")
    st.write("Téléversez un fichier Excel ou ODS contenant un bordereau avec une colonne 'Quantité par taille'.")
    
    uploaded_files = st.file_uploader("Téléverser des fichiers", type=["xlsx", "xls", "ods"], accept_multiple_files=True)
    
    if uploaded_files:
        for uploaded_file in uploaded_files:
            st.subheader(f"Résultats pour : {uploaded_file.name}")
            with st.spinner("Analyse en cours..."):
                if uploaded_file.name.endswith(".ods"):
                    result = process_ods(uploaded_file)
                else:
                    result = process_excel(uploaded_file)

                if isinstance(result, str):
                    st.write(result)
                else:
                    st.table(result)

if __name__ == "__main__":
    main()