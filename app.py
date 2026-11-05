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