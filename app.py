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

#Onglets
onglets = st.tabs([
    "Par abonné",
    "Évolution",
    "Chaleur ou courant ?",
    "Coupures",
    "Relevés hors norme",
])

with onglets[0]:
    st.subheader(f"Quels quartiers consomment le plus par abonné en {annee} ?")
    par_quartier = choix.groupby("quartier")["kwh_par_abonne"].mean().round(1).sort_values()
    st.bar_chart(par_quartier, horizontal=True, y_label="kWh par abonné et par mois")
    par_type = choix.groupby("type")["kwh_par_abonne"].mean().round(1)
    phrase = f"En tête : {par_quartier.index[-1]} ({par_quartier.iloc[-1]} kWh par abonné). "
    if {"Commercial", "Résidentiel"} <= set(par_type.index):
        phrase += (f"Un abonné commercial consomme {par_type['Commercial']} kWh en moyenne, "
                   f"contre {par_type['Résidentiel']} pour un abonné résidentiel.")
    st.write(phrase)

with onglets[1]:
    st.subheader("Comment la consommation évolue-t-elle, commune par commune ?")
    courbes = periode.groupby(["mois", "commune"])["kwh_par_abonne"].mean().unstack()
    st.line_chart(courbes, y_label="kWh par abonné")
    total = periode.pivot_table(index="commune", columns="annee", values="kwh", aggfunc="sum")
    resume = (total[[2024, 2025]] / 1_000_000).round(2)
    resume["hausse_pct"] = ((resume[2025] / resume[2024] - 1) * 100).round(1)
    resume = resume.sort_values("hausse_pct", ascending=False)
    premier = resume.index[0]
    st.write(
        f"Plus forte hausse entre 2024 et 2025 : {premier}, de {resume.loc[premier, 2024]} "
        f"à {resume.loc[premier, 2025]} millions de kWh (+{resume.loc[premier, 'hausse_pct']} %)."
    )
    st.dataframe(resume.rename(columns={"hausse_pct": "hausse (%)"}))

with onglets[2]:
    st.subheader("La consommation suit-elle la chaleur, ou les heures de courant ?")
    residentiel = periode[periode["type"] == "Résidentiel"]
    st.scatter_chart(residentiel, x="heures_courant", y="kwh_par_abonne", color="commune",
                     x_label="Heures de courant par jour", y_label="kWh par abonné")
    r_courant = residentiel["kwh_par_abonne"].corr(residentiel["heures_courant"])
    r_chaleur = residentiel["kwh_par_abonne"].corr(residentiel["temperature_c"])
    st.write(
        f"Quartiers résidentiels, 2024 et 2025 : la corrélation de la consommation par abonné "
        f"est de {r_courant:.2f} avec les heures de courant, et de {r_chaleur:.2f} avec la température."
    )

with onglets[3]:
    st.subheader(f"Où les coupures sont-elles les plus longues en {annee} ?")
    heures = choix.groupby("commune")["heures_courant"].median().round(1).sort_values()
    st.bar_chart(heures, y_label="Médiane des heures de courant par jour")
    courts = choix[choix["heures_courant"] < 8]
    st.write(
        f"Commune avec le moins de courant : {heures.index[0]} "
        f"(médiane de {heures.iloc[0]} heures par jour). "
        f"Relevés de {annee} sous 8 heures de courant : {len(courts)}."
    )
    if len(courts):
        st.dataframe(courts[["mois", "quartier", "heures_courant"]], hide_index=True)

with onglets[4]:
    st.subheader("Quels relevés sortent du lot ?")
    top3 = choix.nlargest(3, "kwh")[["mois", "quartier", "type", "kwh"]]
    st.bar_chart(top3.assign(releve=top3["quartier"] + " " + top3["mois"]),
                 x="releve", y="kwh", y_label="kWh")
    st.write(
        f"La plus grosse consommation de {annee} : {top3.iloc[0]['quartier']} en "
        f"{top3.iloc[0]['mois']} ({top3.iloc[0]['kwh']:,} kWh).".replace(",", " ")
    )
    st.dataframe(top3, hide_index=True)