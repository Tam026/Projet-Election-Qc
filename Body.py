import json
import pandas as pd
import streamlit as st
import geopandas as gpd
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
st.subheader("Élections 2022")

tab1, tab2, tab3, tab4, tab5 = st.tabs([ "Résultats globaux", "Résultats 2022","Carte 2018","Comparaison", "Par région"])

with open("resultats.json", "r", encoding="utf-8") as f:
    data = json.load(f)
df = pd.json_normalize(data["statistiques"]["partisPolitiques"])
gi = pd.json_normalize(data["circonscriptions"])


#st.write(jl.columns)
#st.write(df.columns.tolist())
#st.write(df.head())

c = df.rename(columns = {"nomPartiPolitique": "Parti",
                         "tauxVoteTotal":"Pourcentage de votes",
                         "nbCirconscriptionsEnAvance":"Députés"})

e = gi.rename(columns = {"nomCirconscription" : "Circonscription",
                         "tauxParticipation" : "Taux de participation",
                         "nbElecteurInscrit" : "Nombre d'électeurs inscrits",
                         "candidats" : "Candidats"})

c["Pourcentage de votes"] = pd.to_numeric(c["Pourcentage de votes"])



with open("carte2022simple.kml", "r", encoding="utf-8", errors="ignore") as f:
    kml_pur = f.read()

kml_pur = re.sub(r'&(?![a-zA-Z0-9#]+;)', '&amp;', kml_pur)

gdf_kml = gpd.read_file(io.BytesIO(kml_pur.encode("utf-8")), driver="KML")
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
    
    # 4. Suppression finale de tous les séparateurs pour la fusion des lettres brutes
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
    lambda x: pd.DataFrame(x).sort_values(by="tauxVote", ascending=False).iloc[0]["abreviationPartiPolitique"] if isinstance(x, list) else "Autre"
)

def couleur_parti(row):
        
        if row["Parti"] in ["Coalition avenir Québec - L\u0027équipe François Legault", "C.A.Q.-E.F.L."]:
            return ["background-color : #7AEFFF"]*len(row)

        elif row["Parti"] in ["Parti libéral du Québec/Quebec Liberal Party", "P.L.Q./Q.L.P."]:
             return ["background-color : #FF4749"]*len(row)

        elif row["Parti"] in ["Québec solidaire", "Q.S."]:
             return ["background-color : #FF8A57"]*len(row)

        elif row["Parti"] in ["Parti québécois", "P.Q."]:
             return ["background-color : #4A50FC"]*len(row)

        elif row["Parti"] in ["P.C.Q-E.E.D.", "Parti conservateur du Québec - Équipe Éric Duhaime"]:
            return ["background-color : #585AD5"]*len(row) 

        else:
             return ["background-color : #D8D9DA"]*len(row)

def extraire_couleur_hex(nom_parti):
    style_liste = couleur_parti({"Parti": nom_parti})
    return style_liste[0].split(" : ")[-1]
        

with tab1 :
    st.write("Voici les résultats de l'élection :")
    pourcentage = c["Pourcentage de votes"] > 5
    tableau_resultats = c[pourcentage][["Parti","Pourcentage de votes","Députés"]]
    
    couleurs_part = (tableau_resultats.style
                     .apply(couleur_parti, axis = 1)
                     .map(lambda x : "font-weight: bold", subset="Parti"))
    st.dataframe(couleurs_part, hide_index=True)


with tab2: 
    if "Circonscription" in e.columns :
        donnees2022 = sorted(e["Circonscription"].dropna().unique().tolist())
    circ =st.select_slider("Sélectionnez une circonscription :", options = donnees2022)
    st.write(f"Résultats de la circonscription suivante : {circ}\n")

    circ_select = e[e["Circonscription"]==circ]
    liste_candidats = circ_select["Candidats"].values[0]
    cand = pd.DataFrame(liste_candidats)
    

    with st.sidebar :
            st.title(f"{str(circ).upper()}")
            inscrits = circ_select["Nombre d'électeurs inscrits"].values[0]
            participation = circ_select["Taux de participation"].values[0]
            st.write(f"**Nombre d'électeurs inscrits:** {inscrits}")
            st.write(f"**Taux de participation:** {participation} %")

            if len(carte_fusionnee) == 0:
                st.sidebar.warning("Aucune correspondance trouvée !")
                st.sidebar.write("Exemple KML :", gdf_kml["Name"].head(3).tolist())
                st.sidebar.write("Exemple JSON :", e["Circonscription"].head(3).tolist())
    if not tab2:
         st.sidebar == None            

    h = cand.rename(columns = {"prenom":"Prénom",
                                          "nom" : "Nom",
                                          "abreviationPartiPolitique" : "Parti",
                                          "tauxVote" : "% des votes obtenus ( > 2 % )"})
    
    h = h.sort_values(by="% des votes obtenus ( > 2 % )", ascending =False)
    pourcentage = h["% des votes obtenus ( > 2 % )"]> 2
    tableau_candidats = h[pourcentage][["Nom","Prénom","Parti","% des votes obtenus ( > 2 % )"]]
    gagnant = tableau_candidats["% des votes obtenus ( > 2 % )"].max()

    def gras(row):
         if row["% des votes obtenus ( > 2 % )"] == gagnant:
            return ["font-weight: bold"] * len(row)
         return [""] * len(row)    
    
    cand = (tableau_candidats.style
            .apply(couleur_parti, axis = 1)
            .apply(gras, axis = 1))
    st.dataframe(cand)

   
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

with tab5 :
    st.header("Analyse par région administrative")
              
    regions = e["Circonscription"].apply(harmoniser_nom)
                 
    regions = {"Bas-Saint-Laurent" : ["Matane-Matapédia", "Rimouski", "Rivière-du-Loup–Témiscouata"],
               "Gaspésie-Îles-de-la-Madeleine" : ["Gaspé", "Îles-de-la-Madeleine", "Bonaventure"],
               "Capitale-Nationale" : ["Charlesbourg", "Charlevoix–Côte-de-Beaupré", "Chauveau", "Jean-Lesage", "Jean-Talon", 
                                       "La Peltrie", "Louis-Hébert", "Montmorency", "Portneuf", "Québec", "Tascherau"],
               "Chaudière-Appalaches" :["Beauce-Nord", "Beauce-Sud","Bellechasse","Chutes-de-la-Chaudière","Côte-du-Sud","Lévis","Lotbinière-Frontenac"],
               "Estrie": ["Brome-Missisquoi","Daniel-Johnson","Granby","Mégantic","Orford","Richmond","Saint-François","Sherbrooke"],
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
                              "Sainte-Marie—Saint-Jacques","Viau"].sort(),
                "Outaouais": ["Chapleau","Gatineau","Hull","Papineau","Pontiac"],
                "Abitibi-Témiscamingue": ["Abitibi-Est","Abitibi-Ouest","Rouyn-Noranda–Témiscamingue"],
                "Côte-Nord": ["Duplessis","René-Lévesque"],
                "Nord-du-Québec": ["Duplessis","Ungava"],
                "Saguenay—Lac-Saint-Jean": ["Chicoutimi","Dubuc",'Jonquière',"Lac-Saint-Jean","Roberval"]}

    region_choisie = st.selectbox("Sélectionnez une région administrative :", options=list(regions.keys()))

    region = carte_fusionnee[carte_fusionnee["Circonscription"].isin(regions[region_choisie])]

    if not region.empty:
         recap_parti =region["PartiGagnant"].value_counts().reset_index()
         recap_parti.columns = ["Parti", "Députés obtenus"]
         st.header(f"Résultats pour la région : {region_choisie}")
         st.dataframe(recap_parti, hide_index=True)
    st.bar_chart(data=recap_parti, x="Parti", y="Députés obtenus")
    if region.empty :
        st.info("Aucune donnée disponible pour cette région.")
    
    