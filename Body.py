import json
import pandas as pd
import streamlit as st
import geopandas as gpd
import plotly.express as px
import os
import re
import io
import folium
from streamlit_folium import st_folium
import unicodedata


st.markdown("""
<style>
    .block-container { padding-top: 2rem; }
    .stDataFrame { border-radius: 10px; }
    .stApp { background-color: #EDF4FF; }
    .stSidebar { background-color: #FFFFFF}
</style>
""", unsafe_allow_html=True)

st.set_page_config(page_title="Résultats électoraux Québec 2022", layout="wide")

st.title("Résultats électoraux")
st.header("Québec")
st.subheader("Élections 2018 & 2022")

tab1, tab2, tab3, tab4= st.tabs([ "Résultats globaux", "Résultats 2022","Régions en revue", "Résultats 2018"])

## RESULTATS 2022##
with open("resultats(1).json", "r", encoding="utf-8") as f:
    data = json.load(f)
df = pd.json_normalize(data["statistiques"]["partisPolitiques"])
gi = pd.json_normalize(data["circonscriptions"])


c = df.rename(columns = {"nomPartiPolitique": "Parti",
                         "tauxVoteTotal":"Pourcentage de votes",
                         "nbCirconscriptionsEnAvance":"Députés"})

e = gi.rename(columns = {"nomCirconscription" : "Circonscription",
                         "tauxParticipation" : "Taux de participation",
                         "nbElecteurInscrit" : "Nombre d'électeurs inscrits",
                         "candidats" : "Candidats"})

c["Pourcentage de votes"] = pd.to_numeric(c["Pourcentage de votes"])

##RESULTATS 2018

with open("resultats(2).json", "r", encoding="utf-8") as f:
    data2 = json.load(f)

jk = pd.json_normalize(data2["statistiques"]["partisPolitiques"])
ln = pd.json_normalize(data2["circonscriptions"])

g = jk.rename(columns = {"nomPartiPolitique": "Parti",
                         "tauxVoteTotal":"Pourcentage de votes",
                         "nbCirconscriptionsEnAvance":"Députés"})

i = ln.rename(columns = {"nomCirconscription" : "Circonscription",
                         "tauxParticipation" : "Taux de participation",
                         "nbElecteurInscrit" : "Nombre d'électeurs inscrits",
                         "candidats" : "Candidats"})


g["Pourcentage de votes"] = pd.to_numeric(g["Pourcentage de votes"])
i["Taux de participation"] = pd.to_numeric(i["Taux de participation"])

##RESULTATS 2014
with open("resultats(3).json", "r", encoding="utf-8") as f:
    data2 = json.load(f)

pr = pd.json_normalize(data2["statistiques"]["partisPolitiques"])
su = pd.json_normalize(data2["circonscriptions"])

j = pr.rename(columns = {"nomPartiPolitique": "Parti",
                         "tauxVoteTotal":"Pourcentage de votes",
                         "nbCirconscriptionsEnAvance":"Députés"})

m = su.rename(columns = {"nomCirconscription" : "Circonscription",
                         "tauxParticipation" : "Taux de participation",
                         "nbElecteurInscrit" : "Nombre d'électeurs inscrits",
                         "candidats" : "Candidats"})


j["Pourcentage de votes"] = pd.to_numeric(j["Pourcentage de votes"])
m["Taux de participation"] = pd.to_numeric(m["Taux de participation"])


##Carte
with open("carte2022simple(1).kml", "r", encoding="utf-8", errors="ignore") as f:
    kml_pur = f.read()

gdf_kml = gpd.read_file(io.BytesIO(kml_pur.encode("utf-8-sig")), driver="KML")
carte_fusionnee = gdf_kml.merge(e, left_on="Name", right_on="Circonscription")


def harmoniser_nom(texte):
    if not texte: return ""
    
    # 1. Nettoyage initial : mise en minuscules et retrait des sauts de ligne
    t = str(texte).lower().replace("\n", "").strip()

    t = t.replace("bourassa-sauvé", "bourassa-sauv")
    t = t.replace("îles-de-la-madeleine", "les-de-la-madeleine")
    t = t.replace("la pinire", "la piniere")  
    t = t.replace("mille-les", "mille-iles")
    t = t.replace("notre-dame-de-grce", "notre-dame-de-grace")
    t = t.replace("trois-rivires", "trois-rivieres")
    t = t.replace("vanier-les rivires", "vanier-les rivieres")
    t = t.replace("rivire-du-loup", "riviere-du-loup")
    t = t.replace("tmiscouata", "temiscouata")
    t = t.replace("cte-du-sud", "cote-du-sud")
    t = t.replace("matane-matapdia", "matane-matapedia")
    t = t.replace("tmiscamingue", "temiscamingue")
    t = t.replace("cte-de-beaupr", "cote-de-beaupre")
    t = t.replace("maskinongé", "maskinong")
    t = t.replace("ren-lvesque", "rene-levesque")
    t = t.replace("gaspé", "gasp")
    t = t.replace("lvis", "levis")
    t = t.replace("chteauguay", "chateauguay")
    t = t.replace("jonquire", "jonquiere")
    t = t.replace("hbert", "hebert")
    t = t.replace("prvost", "prevost")
    t = t.replace("jrme", "jerome")
    t = t.replace("franois", "francois")
    t = t.replace("mgantic", "megantic")
    t = t.replace("bcancour", "becancour")
    t = t.replace("chutes-de-la-chaudire", "chutes-de-la-chaudiere")
    t = t.replace("lotbinire", "lotbiniere")
    t = t.replace("verchres", "vercheres")

    # 3. Retrait complet des accents résiduels (Standardisation)
    t = ''.join(c for c in unicodedata.normalize('NFD', t) if unicodedata.category(c) != 'Mn')
    return t.replace(" et ", "").replace("—", "").replace("–", "").replace("-", "").replace(" ", "").replace("'", "").strip()

# Détection automatique de la colonne de nom (Name ou name)
colonne_nom_kml = "Name" if "Name" in gdf_kml.columns else "name"

# Remplissage des colonnes de liaisons nettoyées
gdf_kml["Name_Clean"] = gdf_kml[colonne_nom_kml].apply(harmoniser_nom)
e["Circonscription_Clean"] = e["Circonscription"].apply(harmoniser_nom)

# L'UNIQUE FUSION (Les fusions en double ont été supprimées ici)
carte_fusionnee = gdf_kml.merge(e, left_on="Name_Clean", right_on="Circonscription_Clean")

# Applique le calcul du gagnant sur TOUTES les circonscriptions d'un coup
carte_fusionnee["PartiGagnant"] = carte_fusionnee["Candidats"].apply(
    lambda x: pd.DataFrame(x).sort_values(by="tauxVote", ascending=False).iloc[0]["abreviationPartiPolitique"] if isinstance(x, list) else "Autre")

def couleur_parti(row):
        
        if row["Parti"] in ["Coalition avenir Québec - L\u0027équipe François Legault", "C.A.Q.-E.F.L.","C.A.Q.-É.F.L."]:
            return ["background-color : #7AEFFF"]*len(row)

        elif row["Parti"] in ["Parti libéral du Québec/Quebec Liberal Party", "P.L.Q./Q.L.P."]:
           return ["background-color : #FF4749"]*len(row)

        elif row["Parti"] in ["Québec solidaire", "Q.S."]:
             return ["background-color : #FF8A57"]*len(row)

        elif row["Parti"] in ["Parti québécois", "P.Q."]:
            return ["background-color : #4A50FC"]*len(row)

        elif row["Parti"] in ["P.C.Q-E.E.D.","P.C.Q./C.P.Q.", "Parti conservateur du Québec - Équipe Éric Duhaime"]:
           return ["background-color : #585AD5"]*len(row) 

        else:
            return ["background-color : #D8D9DA"]*len(row)

def couleur_parti_graphique(parti):
        if parti in ["Coalition avenir Québec - L'équipe François Legault", "C.A.Q.-E.F.L.","C.A.Q.-É.F.L."]:
            return "#7AEFFF"
        elif parti in ["Parti libéral du Québec/Quebec Liberal Party", "P.L.Q./Q.L.P."]:
            return "#FF4749"
        elif parti in ["Québec solidaire", "Q.S."]:
            return "#FF8A57"
        elif parti in ["Parti québécois", "P.Q."]:
            return "#4A50FC"
        elif parti in ["Parti conservateur du Québec - Équipe Éric Duhaime", "P.C.Q-E.E.D.", "P.C.Q.-E.E.D.","P.C.Q./C.P.Q."]:
            return "#585AD5"
        else:
            return "#D8D9DA"

def extraire_couleur_hex(nom_parti):
    style_liste = couleur_parti({"Parti": nom_parti})
    return style_liste[0].split(" : ")[-1]
        

with tab1 :

    st.markdown("""
        <style>
        /* 1. Aligner tout le contenu au centre */
        [data-testid="stColumn"] {
            text-align: center;
        }

        /* 2. Titre du parti : Hauteur fixe pour que toutes les images débutent à la même hauteur */
        [data-testid="stColumn"] h3 {
        /* 1. Hauteur généreuse pour accueillir jusqu'à 3 lignes sans décaler la suite */
        height: 95px !important;
        
        /* 2. Flexbox pour centrer le texte verticalement et horizontalement */
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        
        /* 3. Taille de police de vrai sous-titre (1.2rem ~ 19px) */
        font-size: 1.2rem !important;
        font-weight: 700 !important;
        
        /* Rapprochement des lignes pour les acronymes longs sur plusieurs lignes */
        line-height: 1.15 !important;
        text-align: center !important;
        word-break: break-word !important;
        margin-bottom: 10px !important;
    }

        /* 3. Images : Dimensions strictement identiques pour toutes */
        [data-testid="stColumn"] img {
            display: block;
            margin: 0 auto;
            width: 100% !important;
            height: 240px !important;         /* Hauteur fixe pour toutes les photos */
            object-fit: cover !important;     /* Conserve les proportions sans déformer */
            object-position: center top !important; /* Recentre sur les visages */
            border-radius: 8px;
        }

        /* 4. Zone d'infos (après le séparateur) : Hauteur fixe pour que le texte commence au même niveau */
        .info-card {
            min-height: 140px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }
        </style>
    """, unsafe_allow_html=True)
    
    st.write("Voici les résultats des élections générales 2022 :")
    pourcentage = c["Pourcentage de votes"] > 5
    tableau_resultats = c[pourcentage][["Parti","Pourcentage de votes","Députés"]]


    def photo_chef(parti, mot_cle, chef, source_photo):
        try:
                nom_parti = c[c["Parti"].str.contains(mot_cle, regex=False, na=False)]["Parti"].iloc[0]
                couleur_bordure = couleur_parti_graphique(nom_parti)
        except Exception:
                couleur_bordure = "#CCCCCC"

        parti_css= parti.replace(".", "").replace("-", "").replace("/", "").replace(" ", "")

    # st.container crée un cadre unique pour tout le bloc
        with st.container(key=f"parti_{parti_css}"):
            st.markdown(
                    f"""
                    <style>
                    div.st-key-parti_{parti_css} {{
                        border: 3px solid {couleur_bordure} !important;
                        border-radius: 8px !important;
                        padding: 10px !important;
                        box-sizing: border-box;
                    }}
                    </style>
                    """,
                    unsafe_allow_html=True,
                )
            
            base_path = os.path.join("photos", parti)
            ligne = c[c["Parti"].str.contains(mot_cle, regex=False, na=False)]
            st.subheader(f"{mot_cle}")
            
            try:
                st.image(f"{base_path}.jpg", use_container_width=True)
            except Exception:
                try:
                    st.image(f"{base_path}.webp", use_container_width=True)
                except Exception:
                    st.warning("Image introuvable")


            st.markdown(
            f'''
            <div style="position: relative; height: 0px; top: -255px; text-align: right; padding-right: 12px; pointer-events: none; margin-bottom: -355px;">
                <span title="Crédit photo : {source_photo}" 
                    style="pointer-events: auto;
                            cursor: help; 
                            background-color: rgba(0, 0, 0, 0.65); 
                            color: white; 
                            border-radius: 50%; 
                            width: 22px;
                            height: 22px;
                            display: inline-flex;
                            align-items: center;
                            justify-content: center;
                            font-size: 11px; 
                            font-family: serif; 
                            font-weight: bold;
                            box-shadow: 0 1px 3px rgba(0,0,0,0.4);">
                    i
                </span>
            </div>
            ''', 
            unsafe_allow_html=True
        )

            st.divider()

            if f"{parti}" in c.values:
                prct =ligne['Pourcentage de votes'].iloc[0]
                if ligne['Députés'].iloc[0] == 0:
                    st.write(f"{prct:.2f}% des votes obtenus\n\nAucun candidat élu")
                else:
                    st.write(f"{prct:.2f}% des votes obtenus\n\n{ligne['Députés'].iloc[0]} candidats élus")
                st.write(f"Chef: {chef}")

    
    col1, col2, col3, col4, col5 = st.columns(5, gap = "xxsmall")
    with col1:photo_chef("C.A.Q.-E.F.L.", "Coalition avenir Québec - L'équipe François Legault", "François Legault", "La Presse canadienne / Ryan REMIORZ")
    with col2:
        photo_chef("P.L.Q.-Q.L.P.", "Parti libéral du Québec", "Dominique Anglade", "La Presse / Philippe BOIVIN")
        if "P.L.Q./Q.L.P." in c.values:
            ligne_plq = c[c["Parti"].str.contains("Parti libéral du Québec/Quebec Liberal Party", regex=False, na=False)]
            deputes_plq = ligne_plq["Députés"].iloc[0]
            pourcentage_plq = ligne_plq["Pourcentage de votes"].iloc[0]

            if deputes_plq == 0:
                st.warning("Aucun candidat élu")
            else:
                st.write(f"{pourcentage_plq:.2f}% des votes obtenus\n\n{deputes_plq} candidats élus")
            st.write(f"Cheffe: Dominique Anglade")

            
            with st.container(key={"PLQQLP"}):
                
                st.markdown(
                    f"""
                    <style>
                    div.st-key-parti_{"PLQQLP"} {{
                        border: 3px solid {"#FF4749"} !important;
                        border-radius: 8px !important;
                        padding: 10px !important;
                        box-sizing: border-box;
                    }}
                    </style>
                    """,
                    unsafe_allow_html=True,
                )

        
    with col3:photo_chef("Q.S.", "Québec solidaire", "Gabriel Nadeau-Dubois", "Le Devoir / Marie-France COALLIER")
    with col4:photo_chef("P.Q.", "Parti québécois", "Paul St-Pierre Plamondon", "La Presse canadienne / Christinne MUSCHI")
    with col5:photo_chef("P.C.Q-E.E.D.", "Parti conservateur du Québec - Équipe Éric Duhaime", "Éric Duhaime", "Facebook / Éric DUHAIME")


with tab2: 
    if "Circonscription" in e.columns :
        donnees2022 = sorted(e["Circonscription"].dropna().unique().tolist())
        circ =st.select_slider("Sélectionnez une circonscription :", options = donnees2022)
        st.write(f"Résultats de la circonscription suivante : {circ}\n")

    circ_select = e[e["Circonscription"]==circ]
    liste_candidats = circ_select["Candidats"].values[0]
    cand = pd.DataFrame(liste_candidats)

    col1, col2 = st.columns([1,2], gap = "small")

    with col1 :
                st.title(f"{str(circ).upper()}")
                inscrits = circ_select["Nombre d'électeurs inscrits"].values[0]
                insc = f"{inscrits:,}".replace(",", " ")
                participation = float(circ_select["Taux de participation"].values[0])
                st.metric(label="Nombre d'électeurs inscrits : ", value =f"**{insc}**")
                

                if len(carte_fusionnee) == 0:
                    st.warning("Aucune correspondance trouvée !")
                    st.write("Exemple KML :", gdf_kml["Name"].head(3).tolist())
                    st.write("Exemple JSON :", e["Circonscription"].head(3).tolist())

                if participation < 30:
                    st.metric(label="Taux de participation inférieur à 30 %.",value=f"**{participation}%**", delta_color="inverse")
                elif participation > 65:
                    st.metric(label="Taux de participation élevé !", value=f"**{participation}%**", delta_color="normal")
                else:
                    st.metric(label ="Taux de participation modéré.", value =f"**{participation}%**")

                st.divider()
                
                ## COMP
                if ("Circonscription" in e.columns) and ("Circonscription" in i.columns):

                    if circ == "Camille-Laurin":
                        circ_select = e[e["Circonscription"] == "Camille-Laurin"]
                        circ_select2018 = i[i["Circonscription"] == "Bourget"]
                        st.info("Note : Comparaison basée sur l'ancien nom de la circonscription (Bourget).")
                    else:
                        circ_select = e[e["Circonscription"] == circ]
                        circ_select2018 = i[i["Circonscription"] == circ]

                    # 2. Vérification des données 2022
                    if not circ_select.empty:
                        liste_candidats = circ_select["Candidats"].values[0]
                        cand = pd.DataFrame(liste_candidats)
                    else:
                        cand = pd.DataFrame()

                    # 3. Vérification des données 2018
                    if not circ_select2018.empty:
                        liste_candid = circ_select2018["Candidats"].values[0]
                        cand2018 = pd.DataFrame(liste_candid)
                    else:
                        cand2018 = pd.DataFrame()
                        st.warning("Aucune donnée 2018 trouvée pour la comparaison.")

                    if len(cand) >= 2 and len(cand2018) >= 1:
                        gagnant2022 = cand.sort_values(by="tauxVote", ascending=False)
                        gagnant2018 = cand2018.sort_values(by="tauxVote", ascending=False)

                        # Extraction des partis
                        parti_2022 = gagnant2022["abreviationPartiPolitique"].iloc[0]
                        parti_2018 = gagnant2018["abreviationPartiPolitique"].iloc[0]

                        # Normalisation des chaînes pour éviter les pièges d'accents (CAQ)
                        p22_clean = parti_2022.replace("É", "E")
                        p18_clean = parti_2018.replace("É", "E")

                        # --- GESTION DU CHANGEMENT DE PARTI ---
                        if p22_clean == "C.A.Q.-E.F.L." and p18_clean == "C.A.Q.-E.F.L.":
                            st.success("Circonscription conservée par le parti.")
                        elif p18_clean == "C.A.Q.-E.F.L." and p22_clean != "C.A.Q.-E.F.L.":
                            st.error("Défaite du candidat (sortant) de la CAQ.")
                        elif parti_2022 != parti_2018:
                            if parti_2018 == "P.L.Q./Q.L.P.":
                                st.error("Défaite du candidat (sortant) du PLQ.")
                            elif parti_2018 == "Q.S.":
                                st.error("Défaite du candidat (sortant) de QS.")
                            elif parti_2018 == "P.Q.":
                                st.error("Défaite du candidat (sortant) du PQ.")
                            else:
                                st.warning(f"Changement de parti sortant ({parti_2018} -> {parti_2022}).")
                        else:
                            st.success(f"Circonscription conservée par le parti.")

                        # --- CALCUL DE LA LUTTE SERRÉE EN 2022 ---
                        taux_1er = gagnant2022["tauxVote"].iloc[0]
                        taux_2eme = gagnant2022["tauxVote"].iloc[1]
                        ecart_2022 = taux_1er - taux_2eme

                        # Si tauxVote est en pourcentage (ex: 35.5 pour 35.5%), utiliser <= 3
                        # Si tauxVote est entre 0 et 1 (ex: 0.355), utiliser <= 0.03
                        if ecart_2022 <= 3:
                            st.error(f"Lutte serrée! Écart de {ecart_2022:.2f}% entre le 1er et le 2e candidat.")
                        elif ecart_2022 >= 15:
                            st.success(f"Victoire confortable de {ecart_2022:.2f}%")

                    else:
                        st.warning("Données insuffisantes ou nombre de candidats restreint pour effectuer l'analyse complète.")


    with col2 :
        with st.container(border = True):  

            h = cand.rename(columns = {"prenom":"Prénom",
                                                    "nom" : "Nom",
                                                    "abreviationPartiPolitique" : "Parti",
                                                    "tauxVote" : "% des votes obtenus ( > 3 % )"})
            
            h = h.sort_values(by="% des votes obtenus ( > 3 % )", ascending =False)
            pourcentage = h["% des votes obtenus ( > 3 % )"]> 3
            tableau_candidats = h[pourcentage][["Nom","Prénom","Parti","% des votes obtenus ( > 3 % )"]]
            gagnant = tableau_candidats["% des votes obtenus ( > 3 % )"].max()

            nom_sortant2018 = (gagnant2018["nom"].iloc[0])
            prenom_sortant2018 = (gagnant2018["prenom"].iloc[0])
            nom_sortant2022 = (tableau_candidats["Nom"])
            prenom_sortant2022 = (tableau_candidats["Prénom"])


            def asterix(x):
                nom_sortant2022= str(x["Nom"])
                prenom_sortant2022 = str(x["Prénom"])

                if (nom_sortant2018 == nom_sortant2022) and (prenom_sortant2018 == prenom_sortant2022):
                    return f"{nom_sortant2022} *"
                    
                else:
                    return f"{nom_sortant2022}"

            tableau_candidats["Nom"] = tableau_candidats.apply(asterix, axis=1)

            def gras(row):
                if row["% des votes obtenus ( > 3 % )"] == gagnant:
                    return ["font-weight: bold"] * len(row)
                else:
                    return
                
            cand_style = (tableau_candidats.style
                        .format({"% des votes obtenus ( > 3 % )": "{:.2f}"})
                        .apply(couleur_parti, axis = 1)
                        .apply(gras, axis = 1))
            
            st.dataframe(cand_style)
            contient_ast = tableau_candidats["Nom"].str.contains(r"\*").any()

            if contient_ast:
                col_vide, col_info = st.columns([0.7, 0.3])
                with col_info:
                    st.info(" (*) Député sortant (élu en 2018)")
                

            st.divider()
    
            st.subheader(f"Zoom sur {circ}")
            geom = carte_fusionnee[carte_fusionnee["Circonscription"] == circ]

            if not geom.empty:
                    bounds = geom.total_bounds
                    limites_carte = [[bounds[1], bounds[0]], [bounds[3], bounds[2]]]

                    m_zoom = folium.Map(tiles="CartoDB positron")

                    folium.GeoJson(
                        carte_fusionnee,
                        style_function=lambda x: {
                            "fillColor": extraire_couleur_hex(x["properties"].get("PartiGagnant")),
                            "color": "white",
                            "weight": 1,"fillOpacity": 0.6},
                tooltip=folium.GeoJsonTooltip(          #souris n'importe ou = nom
                    fields=["Circonscription", "PartiGagnant"],
                    aliases=["Nom :", "Gagnant 2022 :"]
                )
            ).add_to(m_zoom)

                    # Circonscription sélectionnée (Mise en évidence)
                    folium.GeoJson(
                        geom,
                        style_function=lambda x: {
                            "fillColor": extraire_couleur_hex(x["properties"].get("PartiGagnant")),
                            "color": "#000000",
                            "weight": 3,
                            "fillOpacity": 0.85
                        },
                        tooltip=folium.GeoJsonTooltip(fields=["Circonscription", "PartiGagnant"], aliases=["Nom :", "Gagnant 2022 :"])
                    ).add_to(m_zoom)

                    m_zoom.fit_bounds(limites_carte)
                    st_folium(m_zoom, width=700, height=400, key=f"map_{circ}")
            else:
                    st.warning("Données géographiques introuvables pour cette circonscription.")


with tab3:
    
    data_2022= {"Bas-Saint-Laurent" : ["Matane-Matapédia", "Rimouski", "Rivière-du-Loup–Témiscouata"],
               "Gaspésie-Îles-de-la-Madeleine" : ["Gaspé", "Îles-de-la-Madeleine", "Bonaventure"],
               "Capitale-Nationale" : ["Charlesbourg", "Charlevoix–Côte-de-Beaupré", "Chauveau", "Jean-Lesage", "Jean-Talon", 
                                       "La Peltrie", "Louis-Hébert", "Montmorency", "Portneuf", "Taschereau"],
               "Chaudière-Appalaches" :["Beauce-Nord", "Beauce-Sud","Bellechasse","Chutes-de-la-Chaudière","Côte-du-Sud","Lévis","Lotbinière-Frontenac"],
               "Estrie": ["Brome-Missisquoi","Granby","Mégantic","Orford","Richmond","Saint-François","Sherbrooke"],
               "Centre-du-Québec": ["Arthabaska", "Drummond–Bois-Francs","Drummond–Bois-Francs","Johnson", "Nicolet-Bécancour"],
               "Lanaudière":["Berthier","Joliette","L'Assomption","Masson","Repentigny","Rousseau","Terrebonne"],
               "Mauricie" : ["Champlain","Laviolette–Saint-Maurice","Maskinongé","Trois-Rivières"],
               "Laurentides":["Argenteuil","Bertrand","Blainville", "Deux-Montagnes","Groulx","Mirabel","Prévost","Saint-Jérôme"],
               "Montérégie": ["Beauharnois","Borduas","Chambly","Châteauguay","Huntingdon","Iberville","La Pinière","Laporte",
                              "La Prairie","Marie-Victorin","Montarville","Richelieu","Saint-Hyacinthe","Saint-Jean","Sanguinet",
                              "Soulanges","Taillon","Vachon","Vaudreuil","Verchères"],
                "Laval" : ["Fabre", "Chomedey","Laval-des-Rapides","Mille-Îles","Sainte-Rose","Vimont"],
                "Montréal" : ["Acadie","D'Arcy-McGee","Jacques-Cartier","Marguerite-Bourgeoys","Marquette","Mont-Royal–Outremont",
                              "Nelligan","Notre-Dame-de-Grâce","Robert-Baldwin","Saint-Henri—Sainte-Anne","Saint-Laurent","Verdun",
                              "Westmount—Saint-Louis","Anjou–Louis-Riel","Bourassa-Sauvé","Camille-Laurin","Gouin","Hochelaga-Maisonneuve",
                              "Jeanne-Mance—Viger","LaFontaine","Laurier-Dorion","Maurice-Richard","Mercier","Pointe-aux-Trembles","Rosemont",
                              "Sainte-Marie—Saint-Jacques","Viau"],
                "Outaouais": ["Chapleau","Gatineau","Hull","Papineau","Pontiac"],
                "Abitibi-Témiscamingue": ["Abitibi-Est","Abitibi-Ouest","Rouyn-Noranda–Témiscamingue"],
                "Côte-Nord": ["Duplessis","René-Lévesque"],
                "Nord-du-Québec": ["Duplessis","Ungava"],
                "Saguenay—Lac-Saint-Jean": ["Chicoutimi","Dubuc",'Jonquière',"Lac-Saint-Jean","Roberval"]}
    def sunburst(carte_fusionnee, data_2022, fonction_couleur):
        lignes = []
        for region, circonscriptions in data_2022.items():
            for circ in circonscriptions:
                lignes.append({
                    "Année": "2022",
                    "Région": region,
                    "Circonscription": circ
                })
        df_2022 = pd.DataFrame(lignes)

        df_2022["Circonscription_Clean"] = df_2022["Circonscription"].apply(harmoniser_nom)

        resultats_gagnants = carte_fusionnee[["Circonscription", "PartiGagnant"]].copy()
        resultats_gagnants["Circonscription_Clean"] = resultats_gagnants["Circonscription"].apply(harmoniser_nom)

        df_2022 = df_2022.merge(
            resultats_gagnants[["Circonscription_Clean", "PartiGagnant"]],
            on="Circonscription_Clean",
            how="left"
        )
        df_2022["PartiGagnant"] = df_2022["PartiGagnant"].fillna("Autre")

        # Mapping couleur : un hex par parti gagnant présent dans le dataframe
        partis_presents = df_2022["PartiGagnant"].unique().tolist()
        couleur_map = {parti: couleur_parti_graphique(parti) for parti in partis_presents}

        # 3. Création du graphique Sunburst, coloré par parti gagnant
        fig = px.sunburst(
            data_frame=df_2022,
            path=["Région", "Circonscription"],
            color="PartiGagnant",
            color_discrete_map=couleur_map,
            title="Répartition des circonscriptions selon la région administrative et le parti gagnant (2022)",
            subtitle= "Cliquez sur une région administrative")
        
        fig.update_traces(textinfo="label")
        fig.update_layout(margin=dict(t=40, l=0, r=0, b=0))
        return fig
        

    fig = sunburst(carte_fusionnee, data_2022, couleur_parti_graphique)
    st.plotly_chart(fig, use_container_width=True)

with tab4:

    if "Circonscription" in i.columns :
        donnees2018 = sorted(i["Circonscription"].dropna().unique().tolist())
    circ2018 = st.select_slider("Sélectionnez une circonscription :", options = donnees2018)
    st.write(f"Résultats de la circonscription suivante : {circ2018}\n")

    circ_select2018 = i[i["Circonscription"]==circ2018]
    if not circ_select2018.empty:
        inscrits = circ_select2018["Nombre d'électeurs inscrits"].values[0]
        participation = float(circ_select2018["Taux de participation"].values[0])

    liste_candid = circ_select2018["Candidats"].values[0]
    cand2018 = pd.DataFrame(liste_candid)

    # --- 2. PRÉPARATION ET EXTRACTION DU GAGNANT 2014 ---
    gagnant2014 = None
    nom_sortant2014 = ""
    prenom_sortant2014 = ""

    if "Circonscription" in m.columns:
        # CORRECTION : Filtrer 2014 sur la circonscription sélectionnée
        circ_select2014 = m[m["Circonscription"] == circ2018]
        if not circ_select2014.empty:
            liste_candid2014 = circ_select2014["Candidats"].values[0]
            cand2014 = pd.DataFrame(liste_candid2014)
            if not cand2014.empty:
                gagnant2014 = cand2014.sort_values(
                    by="tauxVote", ascending=False
                )
                # Extraire et nettoyer les identifiants du gagnant 2014
                nom_sortant2014 = (
                    str(gagnant2014["nom"].iloc[0]).strip().lower()
                )
                prenom_sortant2014 = (
                    str(gagnant2014["prenom"].iloc[0]).strip().lower()
                )   

    col3, col4 = st.columns([1,2], gap = "small", border = False)

    with col3 :
            st.title(f"{str(circ2018).upper()}")
            inscrits = circ_select2018["Nombre d'électeurs inscrits"].values[0]
            insc = f"{inscrits:,}".replace(",", " ")
            participation = circ_select2018["Taux de participation"].values[0]
            st.metric(label="Nombre d'électeurs inscrits : ", value =f"**{insc}**")

            if len(carte_fusionnee) == 0:
                st.warning("Aucune correspondance trouvée !")
                st.write("Exemple KML :", gdf_kml["Name"].head(3).tolist())
                st.write("Exemple JSON :", i["Circonscription"].head(3).tolist())

            if participation < 30:
                st.metric(label="Taux de participation inférieur à 30 %.",value=f"**{participation}%**", delta_color="inverse")
            elif participation > 65:
                st.metric(label="Taux de participation élevé !", value=f"**{participation}%**", delta_color="normal")
            else:
                st.metric(label="Taux de participation modéré.", value=f"**{participation}%**", delta_color = "off")

            st.divider()

            if len(cand2018) >= 2 and gagnant2014 is not None:
                gagnant2018 = cand2018.sort_values(by="tauxVote", ascending=False)

                parti_2014 = gagnant2014["abreviationPartiPolitique"].iloc[0]
                parti_2018 = gagnant2018["abreviationPartiPolitique"].iloc[0]

                p14_clean = parti_2014.replace("É", "E")
                p18_clean = parti_2018.replace("É", "E")
            
            
# --- GESTION DU CHANGEMENT DE PARTI ---
                if p18_clean == "C.A.Q.-E.F.L." and p14_clean == "C.A.Q.-E.F.L.":
                        st.success("Circonscription conservée par le parti.")
                elif p18_clean == "C.A.Q.-E.F.L." and p14_clean != "C.A.Q.-E.F.L.":
                    st.error("Défaite du candidat (sortant) de la CAQ.")
                elif p14_clean != p18_clean:
                    if parti_2014 == "P.L.Q./Q.L.P.":
                        st.error("Défaite du candidat (sortant) du PLQ.")
                    elif parti_2014 == "Q.S.":
                        st.error("Défaite du candidat (sortant) de QS.")
                    elif parti_2014 == "P.Q.":
                        st.error("Défaite du candidat (sortant) du PQ.")
                    else:
                        st.warning(f"Changement de parti sortant ({parti_2014} -> {parti_2018}).")
                else:
                    st.success(f"Circonscription conservée par le parti.")

                        # --- CALCUL DE LA LUTTE SERRÉE EN 2018 ---
                taux_1er = gagnant2018["tauxVote"].iloc[0]
                taux_2eme = gagnant2018["tauxVote"].iloc[1]
                ecart_2018 = taux_1er - taux_2eme

                        # Si tauxVote est en pourcentage (ex: 35.5 pour 35.5%), utiliser <= 3
                        # Si tauxVote est entre 0 et 1 (ex: 0.355), utiliser <= 0.03
                if ecart_2018 <= 3:
                    st.error(f"Lutte serrée ! Écart de {ecart_2018:.2f}% entre le 1er et le 2e candidat.")
                elif ecart_2018 >= 15:
                    st.success(f"Victoire confortable de {ecart_2018:.2f}%")

            else:
                st.warning("Données insuffisantes ou nombre de candidats restreint pour effectuer l'analyse complète.")
                        
    with col4 : 

        with st.container(border = True):

            h2018 = cand2018.rename(columns = {"prenom":"Prénom",
                                                                "nom" : "Nom",
                                                                "abreviationPartiPolitique" : "Parti",
                                                                "tauxVote" : "% des votes obtenus ( > 3 % )"})          

            h2018 = h2018.sort_values(by="% des votes obtenus ( > 3 % )", ascending =False)
            pourcentage = h2018["% des votes obtenus ( > 3 % )"]> 3
            tableau_candidats = h2018[pourcentage][["Nom","Prénom","Parti","% des votes obtenus ( > 3 % )"]]
            gagnant = tableau_candidats["% des votes obtenus ( > 3 % )"].max()

            #h2014 = cand2014.rename(columns = {"prenom":"Prénom",
                                #                                "nom" : "Nom",
                                 #                               "abreviationPartiPolitique" : "Parti",
                                  #                              "tauxVote" : "% des votes obtenus ( > 3 % )"})

            #h2014 = h2014.sort_values(by="% des votes obtenus ( > 3 % )", ascending =False)
            #pourcentage2014 = h2014["% des votes obtenus ( > 3 % )"]> 3
            #tableau_candidats_2014 = h2014[pourcentage][["Nom","Prénom","Parti","% des votes obtenus ( > 3 % )"]]
            #gagnant_2014 = tableau_candidats_2014["% des votes obtenus ( > 3 % )"].max()
        

            nom_sortant2018 = (tableau_candidats["Nom"])
            prenom_sortant2018 = (tableau_candidats["Prénom"])
            nom_sortant2014 = (gagnant2014["nom"].iloc[0])
            prenom_sortant2014 = (gagnant2014["prenom"].iloc[0])


            def asterix(x):
                nom_sortant2018= str(x["Nom"]).strip()
                prenom_sortant2018 = str(x["Prénom"]).strip()


                if (nom_sortant2018 == nom_sortant2014) and (prenom_sortant2018 == prenom_sortant2014):
                    return f"{nom_sortant2018} *"
                    
                else:
                    return f"{nom_sortant2018}"

            tableau_candidats["Nom"] = tableau_candidats.apply(asterix, axis=1)

            
            def gras(row):
                if row["% des votes obtenus ( > 3 % )"] == gagnant:
                    return ["font-weight: bold"] * len(row)
                return [""] * len(row)    
                    
            cand2018 = (tableau_candidats.style
                            .format({"% des votes obtenus ( > 3 % )": "{:.2f}"})
                            .apply(couleur_parti, axis = 1)
                            .apply(gras, axis = 1))

            st.dataframe(cand2018)
            contient_ast = tableau_candidats["Nom"].str.contains(r"\*").any()

            if contient_ast:
                col_vide, col_info = st.columns([0.7, 0.3])
                with col_info:
                    st.info(" (*) Député sortant (élu en 2014)")

            st.divider()
                
            st.subheader(f"Zoom sur {circ2018}")
            geom = carte_fusionnee[carte_fusionnee["Circonscription"] == circ2018]
            
            if not geom.empty:
                bounds = geom.total_bounds
                limites_carte = [[bounds[1], bounds[0]], [bounds[3], bounds[2]]]
            
                m_zoom = folium.Map(tiles="CartoDB positron")
            
                folium.GeoJson(
                            carte_fusionnee,
                            style_function=lambda x: {
                                "fillColor": extraire_couleur_hex(x["properties"].get("PartiGagnant")),
                                "color": "white",
                                "weight": 1,"fillOpacity": 0.6},
                    tooltip=folium.GeoJsonTooltip(          #souris n'importe ou = nom
                        fields=["Circonscription", "PartiGagnant"],
                        aliases=["Nom :", "Gagnant 2018 :"]
                    )
                ).add_to(m_zoom)

                        # Circonscription sélectionnée (Mise en évidence)
                folium.GeoJson(geom,
                            style_function=lambda x: {
                                "fillColor": extraire_couleur_hex(x["properties"].get("PartiGagnant")),
                                "color": "#000000",
                                "weight": 3,
                                "fillOpacity": 0.85
                            },
                            tooltip=folium.GeoJsonTooltip(fields=["Circonscription", "PartiGagnant"], aliases=["Nom :", "Gagnant 2018 :"])
                        ).add_to(m_zoom)
            
                m_zoom.fit_bounds(limites_carte)
                st_folium(m_zoom, width=700, height=400, key=f"map_{circ2018}")
            else:
                st.warning("Données géographiques introuvables pour cette circonscription.")


