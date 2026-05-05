# SmartARS

**Robot de Veille Réglementaire** — Analyse automatique des RAA (Recueils des Actes Administratifs) pour extraire les autorisations d'équipements d'imagerie médicale lourde (EML) en France.

---

## Ce que fait SmartARS

1. **Scrape** les sites des 17 préfectures régionales françaises
2. **Filtre** les RAA du mois/année demandé
3. **Analyse** le contenu PDF pour trouver les autorisations d'équipements lourds
4. **Génère** un PDF par RAA pertinent (couverture + sommaire + pages d'autorisations)
5. **Consolide** tous les résultats dans un fichier Excel unique

---

## Installation (Windows)

### Prérequis

- **Python 3.10+** installé — [Télécharger Python](https://www.python.org/downloads/)

```powershell
python --version
```

### Mise en place

```powershell
# Cloner le projet
git clone https://github.com/arquam-elglaoui/SmartARS.git
cd SmartARS

# Créer l'environnement virtuel (une seule fois)
python -m venv env

# Activer l'environnement (à faire à chaque session)
.\env\Scripts\activate

# Installer les dépendances
pip install -r requirements.txt
```

---

## Utilisation

**Toujours activer l'environnement d'abord :**

```powershell
cd "C:\Dev\Source\Repos\SmartARS"
.\env\Scripts\activate
```

### Mode interactif (recommandé)

```powershell
python main.py
```

Un menu guidé permet de sélectionner les mois, années et régions.

### Ligne de commande

```powershell
python main.py 11 2025                   # Un mois, toutes régions
python main.py 10,11,12 2025             # Plusieurs mois
python main.py 11 2024,2025              # Plusieurs années
python main.py 11 2025 bretagne paca     # Régions spécifiques
python main.py 11 2025 --force           # Ignorer le cache
```

### Interface graphique

```powershell
python smartars_gui.py
```

Fonctionnalités : sélection multiple mois/régions, progression en temps réel, accès direct aux résultats et à l'Excel.

---

## Paramètres

| Paramètre    | Format                          | Exemples                          |
|--------------|---------------------------------|-----------------------------------|
| **Mois**     | Numéro ou nom, virgule pour multiples | `11`, `novembre`, `10,11,12` |
| **Année**    | AAAA, virgule pour multiples    | `2025`, `2024,2025`               |
| **Régions**  | Noms séparés par espaces        | `bretagne paca normandie`         |
| **--force**  | Ignorer le cache anti-doublons  |                                   |

---

## Résultats

Tous les résultats sont dans `~/Documents/SmartARS/`.

```
Documents/SmartARS/
├── SmartARS_Historique.xlsx            # Fichier principal (toutes les données)
└── results/
    └── 2025_decembre/                  # Un dossier par mois analysé
        ├── smartars.log                # Log de l'exécution
        ├── bretagne/
        │   ├── log_bzh_decembre_2025.txt
        │   └── RAA_029_2025_0042_EXTRACT.pdf
        └── ile-de-france/
            ├── log_idf_decembre_2025.txt
            └── RAA_075_2025_0123_EXTRACT.pdf
```

### Fichier Excel

- **Une feuille par mois** (ex: `2025_novembre`)
- **Colonnes** : Region, Source, Page, Equipements, Etablissement, Code_Postal, URL
- **Anti-doublons** : les entrées existantes ne sont pas recréées

### PDFs extraits

Chaque PDF contient la couverture + le sommaire du RAA original + les pages d'autorisations.

---

## Équipements recherchés

| Mot-clé                     | Description                              |
|-----------------------------|------------------------------------------|
| IRM                         | Imagerie par Résonance Magnétique        |
| Scanner / Scanographe       | Tomodensitométrie                        |
| TEP                         | Tomographie par Émission de Positons     |
| Gamma                       | Caméra à scintillation                   |
| Tomographe                  | Appareil de tomographie                  |
| Radiologie                  | Équipements radiologiques                |
| Imagerie en coupes           | Modalités d'imagerie en coupes           |
| Bilan Quantitatif/Quantifié | Documents de bilan EML                   |

---

## Régions couvertes (17)

| Région                        | Identifiant commande       |
|-------------------------------|----------------------------|
| Auvergne-Rhône-Alpes          | `auvergne-rhone-alpes`     |
| Bourgogne-Franche-Comté       | `bourgogne-franche-comte`  |
| Bretagne                      | `bretagne`                 |
| Centre-Val de Loire           | `centre-val-de-loire`      |
| Corse                         | `corse`                    |
| Grand Est                     | `grand-est`                |
| Guadeloupe                    | `guadeloupe`               |
| Guyane                        | `guyane`                   |
| Hauts-de-France               | `hauts-de-france`          |
| Île-de-France                 | `ile-de-france`            |
| Martinique                    | `martinique`               |
| Normandie                     | `normandie`                |
| Nouvelle-Aquitaine            | `nouvelle-aquitaine`       |
| Occitanie                     | `occitanie`                |
| Pays de la Loire              | `pays-de-la-loire`         |
| Provence-Alpes-Côte d'Azur    | `paca`                     |
| La Réunion                    | `reunion`                  |

> **Note La Réunion** : publie les RAA du mois le 1er ou 2 du mois suivant.

---

## Structure du code

```
SmartARS/
├── main.py              # Point d'entrée CLI (menu interactif + orchestration)
├── smartars_gui.py      # Interface graphique (CustomTkinter)
├── config.py            # Configuration : mots-clés, timeouts, mois
├── utils.py             # Façade utilitaires (HTTP, ré-exports)
├── date_utils.py        # Normalisation mois, accents, validation dates
├── pdf_analyzer.py      # Analyse du contenu PDF (détection équipements)
├── pdf_extractor.py     # Création des PDFs extraits (sommaire + pages)
├── analyzer.py          # Orchestration analyse par région + logs
├── cache.py             # Cache anti-doublons (JSON)
├── excel_export.py      # Export Excel historique unique
├── build_exe.py         # Script de build PyInstaller
├── requirements.txt     # Dépendances Python
├── README.md            # Ce fichier
└── regions/             # Un extracteur par région (17 fichiers)
    ├── __init__.py
    ├── bretagne.py
    ├── ile_de_france.py
    └── ...
```

---

## Configuration avancée

Éditer `config.py` pour modifier :

- `KEYWORDS_REGEX` : Patterns de détection des équipements
- `KEYWORDS_AUTORISATION` : Mots confirmant une autorisation
- `TIMEOUT_PAGE` / `TIMEOUT_PDF` : Délais de téléchargement (30s / 120s)
- `MAX_RETRIES` : Nombre de tentatives en cas d'échec (3)

---

## Créer un exécutable (.exe)

```powershell
.\env\Scripts\activate
python build_exe.py
```

L'exécutable est créé dans `dist/SmartARS.exe`. Aucune installation requise sur les postes utilisateurs.

---

## Dépannage

| Problème                            | Solution                                              |
|-------------------------------------|-------------------------------------------------------|
| `python n'est pas reconnu`          | Réinstaller Python en cochant "Add to PATH"           |
| `No module named 'requests'`        | `.\env\Scripts\activate` puis `pip install -r requirements.txt` |
| 0 PDF trouvé pour une région        | Pas de RAA ce mois, ou site de la préfecture modifié  |
| Erreur de téléchargement / Timeout  | 3 tentatives automatiques. Site peut-être indisponible |
| Relancer un mois déjà analysé       | Ajouter `--force` à la commande                       |

---

## Licence

Projet interne — Usage privé.
