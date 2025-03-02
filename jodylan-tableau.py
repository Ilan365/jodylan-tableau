import streamlit as st
import pandas as pd
import re

# Définition des catégories de tailles
size_categories = {
    "34/36 et 46/48": [34, 36, 46, 48],
    "38/40 et 42/44": [38, 40, 42, 44],
    "50/52": [50, 52],
    "54/56": [54, 56],
    "58/60": [58, 60],
    "62/64": [62, 64],
}

def extract_quantity_and_size(text):
    """Extrait la quantité et la taille d'une chaîne de type '30 taille 36'."""
    matches = re.findall(r'(\d+)\s+taille\s+(\d+)', text)
    return [(int(quantity), int(size)) for quantity, size in matches]

def process_excel(file):
    """Traite un fichier Excel ou CSV et regroupe les quantités par fourchette de tailles."""
    if file.name.endswith(".csv"):
        df = pd.read_csv(file)
    else:
        df = pd.read_excel(file, engine='openpyxl')  # Charge uniquement la première feuille
    
    size_totals = {key: 0 for key in size_categories}
    
    # Vérifier la présence de la colonne attendue
    if "Quantité par taille" not in df.columns:
        return "Erreur : Colonne 'Quantité par taille' non trouvée. Vérifie le fichier."
    
    # Parcourir chaque ligne
    for row in df["Quantité par taille"].dropna():
        extracted_data = extract_quantity_and_size(str(row))
        for quantity, size in extracted_data:
            for category, sizes in size_categories.items():
                if size in sizes:
                    size_totals[category] += quantity
                    break
    
    # Ajout du total des articles
    total_articles = sum(size_totals.values())
    
    result_df = pd.DataFrame(list(size_totals.items()), columns=["Fourchette de tailles", "Nombre total de pièces"])
    result_df.loc[len(result_df)] = ["Total d'articles", total_articles]
    
    return result_df

def main():
    st.title("Analyse automatique des bordereaux")
    st.write("Téléversez un ou plusieurs fichiers Excel ou CSV contenant un tableau avec une colonne 'Quantité par taille'.")
    
    uploaded_files = st.file_uploader("Téléverser des fichiers", type=["xlsx", "xls", "csv"], accept_multiple_files=True)
    
    if uploaded_files:
        for uploaded_file in uploaded_files:
            st.subheader(f"Résultats pour : {uploaded_file.name}")
            with st.spinner("Analyse en cours..."):
                result = process_excel(uploaded_file)
                if isinstance(result, str):
                    st.write(result)  # Affiche un message d'erreur si applicable
                else:
                    st.table(result)

if __name__ == "__main__":
    main()
