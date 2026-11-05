from pathlib import Path

import pandas as pd
import streamlit as st

DOSSIER = Path(__file__).parent / "donnees"

st.set_page_config(page_title="L'électricité dans 12 quartiers", page_icon="⚡", layout="wide")


@st.cache_data
def charger():
    return pd.read_csv(DOSSIER / "consommation_propre.csv")


donnees = charger()

st.title("L'électricité dans 12 quartiers")
st.caption("Relevés mensuels de janvier 2024 à décembre 2025. Données fictives.")
st.write(
    "Une compagnie d'électricité suit 12 quartiers de Port-au-Prince, Delmas, Pétion-Ville "
    "et Cap-Haïtien. Question du directeur : la consommation suit-elle la chaleur, "
    "ou les heures de courant ?"
)


communes_dispo = sorted(donnees["commune"].unique())
communes = st.sidebar.multiselect("Communes", communes_dispo, default=communes_dispo)

annees = sorted(donnees["annee"].unique())
annee = st.sidebar.selectbox("Année", annees, index=annees.index(2025))

if not communes:
    st.warning("Choisissez au moins une commune dans la barre latérale.")
    st.stop()


periode = donnees[donnees["commune"].isin(communes)]
choix = periode[periode["annee"] == annee]

#Indicateurs
col1, col2, col3 = st.columns(3)
col1.metric(f"Consommation {annee}", f"{choix['kwh'].sum() / 1_000_000:.2f} millions de kWh")
col2.metric("Par abonné et par mois", f"{choix['kwh_par_abonne'].mean():.1f} kWh")
col3.metric("Courant par jour", f"{choix['heures_courant'].mean():.1f} heures")