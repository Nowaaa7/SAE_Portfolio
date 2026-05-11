#!/usr/bin/python3

import pandas as pd
import requests
import json
import os
from subprocess import run
import argparse
from create_ascii_chart import draw

parser = argparse.ArgumentParser(description = "Download .cvs and get top N (default 10) groups")
parser.add_argument("-l", "--link", type = str, nargs = "?", default = "https://www.data.gouv.fr/api/1/datasets/r/880cca20-3300-4f93-8b67-4de515b42dc9", help = "Use custom link to download dataset")
parser.add_argument("-n", "--number", type = int, nargs = "?", default = 10, help = "Use custom number of groups to chart")
parser.add_argument("-a", "--ascii", type = int, nargs = "?", default = 1, help = "Use -a0 to turn off ascii chart")
parser.add_argument("-q", "--quickchart", type = int, nargs = "?", default = 1, help = "Use -q0 to turn off QuickChart")
parser.add_argument("-o", "--open_quickchart", type = int, nargs = "?", default = 1, help = "Use -o0 to prevent script from opening QuickChart image automatically.")
args = parser.parse_args()

do_ascii = bool(args.ascii)
do_quickchart = bool(args.quickchart)

# ÉTAPE 1 : CHARGEMENT DES DONNÉES
nom_fichier = 'clubs-data-2023.csv'
adresse_fichier = args.link

print(f" Chargement du fichier {nom_fichier}...")

data = requests.get(adresse_fichier)
with open(nom_fichier, "wb") as file:
    file.write(data.content)

# On vérifie si le fichier existe
if not os.path.exists(nom_fichier):
    print(f" ERREUR : Le fichier '{nom_fichier}' est introuvable !")
    print(" Assure-toi qu'il est bien dans le même dossier que ce script.")
    exit()

try:
    # Le fichier utilise des points-virgules comme séparateur
    df = pd.read_csv(nom_fichier, sep=';')
    print(" Fichier chargé avec succès !")
    print(f"   Total de lignes : {len(df)}")
    print(f"   Colonnes : {', '.join(df.columns)}")
except Exception as e:
    print(f" Erreur lors de la lecture du CSV : {e}")
    exit()

# ÉTAPE 2 : CALCULS (Top N des Fédérations)
print("\n Calcul des statistiques en cours...")

# On groupe par "Fédération" et on additionne la colonne "Total" (Clubs + EPA)
# On trie du plus grand au plus petit et on garde les N premiers

groups_number = args.number

top = df.groupby('Fédération')['Total'].sum().sort_values(ascending=False).head(groups_number)

top_list = [list(dict(top).keys()), list(top)]


if do_quickchart:
    # On prépare les listes pour le graphique
    noms_fedes = top.index.tolist()   # Axe X (Noms)
    nb_structures = top.values.tolist() # Axe Y (Chiffres)

    print(" Top 3 des fédérations trouvées :")
    for i in range(3):
        print(f"   {i+1}. {noms_fedes[i]} ({nb_structures[i]} structures)")

    # ÉTAPE 3 : GÉNÉRATION DU GRAPHIQUE (QuickChart.io)
    print("\n Création du graphique...")

    # Configuration JSON pour QuickChart
    chart_config = {
        "type": "bar",
        "data": {
            "labels": noms_fedes, # Les noms des fédés
            "datasets": [{
                "label": "Nombre de Clubs & Établissements (2023)",
                "data": nb_structures, # Les chiffres
                "backgroundColor": "rgba(54, 162, 235, 0.6)", # Bleu joli
                "borderColor": "rgba(54, 162, 235, 1)",
                "borderWidth": 1
            }]
        },
        "options": {
            "title": {
                "display": True,
                "text": "Top 10 des Fédérations Sportives (Nombre de structures)"
            },
            "scales": {
                "yAxes": [{
                    "ticks": {
                        "beginAtZero": True
                    }
                }]
            }
        }
    }

    # Envoi à l'API
    url_api = "https://quickchart.io/chart/create"
    payload = {
        "chart": chart_config,
        "width": 800,
        "height": 500,
        "backgroundColor": "white"
    }

    try:
        response = requests.post(url_api, json=payload)
        
        if response.status_code == 200:
            resultat = response.json()
            print("\n SUCCÈS TOTAL ! ")
            print("Clique sur ce lien pour voir ton graphique :")
            quickchart_link = resultat['url']
            print(quickchart_link)
        else:
            print(" Erreur de l'API QuickChart :", response.text)

    except Exception as e:
        print(f" Erreur de connexion Internet : {e}")

if do_ascii:       #Printing ASCII chart
    print('\n') 
    draw(top_list)

#Downloading Quickchart
if do_quickchart and args.open_quickchart:
    qc_chart = requests.get(quickchart_link)
    with open('QuickChart_chart.png', 'wb') as file:
        file.write(qc_chart.content)
        file.close()
    run(['xdg-open', 'QuickChart_chart.png'])

