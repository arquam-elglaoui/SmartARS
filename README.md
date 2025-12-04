# SmartARS 🏥

**Robot de Veille Réglementaire** - Analyse automatique des RAA (Recueils des Actes Administratifs) pour trouver les autorisations d'équipements d'imagerie médicale lourde en France.

---

## 📋 Fonctionnalités

- ✅ Scraping automatique des 17 préfectures régionales françaises
- ✅ Détection des autorisations d'équipements lourds (IRM, Scanner, TEP, etc.)
- ✅ Génération d'un **PDF de synthèse** par région (page de garde + sommaire + pages d'autorisations)
- ✅ Export **Excel** avec détails (établissement, code postal, page, équipement)
- ✅ Système anti-doublons (cache des URLs déjà traitées)
- ✅ Mode interactif ou ligne de commande

---

## 🚀 Installation

### Prérequis
- Python 3.10+
- pip

### Installation des dépendances

```bash
cd SmartARS
python -m venv env
env\Scripts\activate   # Windows
pip install -r requirements.txt
```

---

## 💻 Utilisation

### Mode Interactif (recommandé)
```bash
python main.py
```
Un menu s'affiche pour choisir le mois, l'année et les régions.

### Ligne de commande
```bash
# Toutes les régions
python main.py novembre 2025

# Avec numéro de mois
python main.py 11 2025

# Régions spécifiques
python main.py novembre 2025 bretagne ile-de-france

# Forcer la ré-analyse (ignorer le cache)
python main.py novembre 2025 --force
```

---

## 📂 Structure des résultats

```
~/Documents/SmartARS/
├── results/
│   └── 2025_novembre/
│       ├── RECAP_2025_novembre.xlsx      # Récapitulatif global
│       ├── smartars.log                   # Log d'exécution
│       ├── bretagne/
│       │   ├── Autorisations_bretagne.pdf
│       │   └── Resultats_bretagne.xlsx
│       ├── ile-de-france/
│       │   ├── Autorisations_ile-de-france.pdf
│       │   └── Resultats_ile-de-france.xlsx
│       └── ...
└── .cache.json                            # Cache anti-doublons
```

---

## 🔍 Équipements détectés

| Mot-clé | Description |
|---------|-------------|
| IRM | Imagerie par Résonance Magnétique |
| Scanner / Scanographe | Tomodensitométrie |
| TEP | Tomographie par Émission de Positons |
| Gamma | Caméra à scintillation / Gamma caméra |
| Tomographe | Appareil de tomographie |
| Radiologie | Équipements radiologiques |
| Imagerie en coupes | Modalités d'imagerie en coupes |

---

## 🗺️ Régions couvertes

| # | Région | Source |
|---|--------|--------|
| 1 | Auvergne-Rhône-Alpes | Préfecture de région |
| 2 | Bourgogne-Franche-Comté | Préfecture de région |
| 3 | Bretagne | Préfecture de région |
| 4 | Centre-Val de Loire | Préfecture de région |
| 5 | Corse | Préfectures 2A et 2B |
| 6 | Grand Est | Préfecture de région |
| 7 | Guadeloupe | Préfecture |
| 8 | Guyane | Préfecture |
| 9 | Hauts-de-France | Préfecture de région |
| 10 | Île-de-France | Préfecture de région |
| 11 | Martinique | Préfecture |
| 12 | Normandie | Préfecture de région |
| 13 | Nouvelle-Aquitaine | Préfecture de région |
| 14 | Occitanie | Préfecture de région |
| 15 | Pays de la Loire | Préfecture de région |
| 16 | Provence-Alpes-Côte d'Azur | Préfecture de région |
| 17 | La Réunion | Préfecture |

---

## 📁 Structure du projet

```
SmartARS/
├── main.py              # Point d'entrée principal
├── config.py            # Configuration (mots-clés, timeouts)
├── utils.py             # Fonctions utilitaires (scraping, analyse PDF)
├── requirements.txt     # Dépendances Python
├── README.md            # Ce fichier
└── regions/             # Extracteurs par région
    ├── __init__.py
    ├── bretagne.py
    ├── ile_de_france.py
    └── ...
```

---

## ⚙️ Configuration

Éditer `config.py` pour personnaliser :

- `KEYWORDS_REGEX` : Patterns de détection des équipements
- `KEYWORDS_AUTORISATION` : Mots-clés pour valider une autorisation
- `TIMEOUT_PAGE` / `TIMEOUT_PDF` : Délais de téléchargement
- `DELAY_BETWEEN_REQUESTS` : Pause entre requêtes (respect serveurs)

---

## 📝 Logs

Les logs sont enregistrés dans :
```
~/Documents/SmartARS/results/{annee}_{mois}/smartars.log
```

Format :
```
2025-12-04 10:30:15 - INFO - Debut analyse: bretagne
2025-12-04 10:30:18 - INFO - bretagne: 3 PDF a analyser
2025-12-04 10:30:45 - INFO - bretagne: 2 autorisation(s) trouvee(s)
```

---

## 🔧 Dépendances

```
requests>=2.31.0
beautifulsoup4>=4.12.0
pandas>=2.0.0
openpyxl>=3.1.0
PyMuPDF>=1.23.0
```

---

## 📄 Licence

Projet interne - Usage privé.

---

## 👤 Auteur

SmartARS - Robot de veille réglementaire pour l'imagerie médicale.

