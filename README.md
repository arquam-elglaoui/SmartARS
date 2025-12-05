# SmartARS 🏥

**Robot de Veille Réglementaire** - Analyse automatique des RAA (Recueils des Actes Administratifs) pour extraire les autorisations d'équipements d'imagerie médicale lourde (EML) en France.

---

## 📋 Ce que fait SmartARS

1. **Scrape** les sites des 17 préfectures régionales françaises
2. **Filtre** les RAA du mois/année demandé
3. **Analyse** le contenu PDF pour trouver les autorisations d'équipements lourds
4. **Génère** un PDF par RAA pertinent (pages 1-3 + pages d'autorisations)
5. **Consolide** tous les résultats dans un fichier Excel unique

---

## 🚀 Installation (Windows)

### Étape 1 : Prérequis

- **Python 3.10+** installé → [Télécharger Python](https://www.python.org/downloads/)
- Vérifier l'installation :
```powershell
python --version
```

### Étape 2 : Télécharger le projet

```powershell
# Option A : Cloner depuis GitHub
git clone https://github.com/arquam-elglaoui/SmartARS.git
cd SmartARS

# Option B : Télécharger le ZIP depuis GitHub et extraire
```

### Étape 3 : Créer l'environnement virtuel

```powershell
# Créer l'environnement (une seule fois)
python -m venv env

# Activer l'environnement (à faire à chaque session)
.\env\Scripts\activate

# Tu verras (env) apparaître au début de la ligne
```

### Étape 4 : Installer les dépendances

```powershell
pip install -r requirements.txt
```

✅ **C'est prêt !**

---

## 💻 Comment lancer SmartARS

### ⚠️ IMPORTANT : Toujours activer l'environnement d'abord !

```powershell
cd "C:\Program Files\SmartARS"    # ou ton chemin
.\env\Scripts\activate             # Active l'environnement
```

Tu dois voir `(env)` au début de ta ligne de commande.

---

### Option 1 : Mode Interactif (recommandé pour débuter)

```powershell
python main.py
```

Un menu s'affiche :
```
============================================================
   SmartARS - Robot de Veille Reglementaire
============================================================

Mois disponibles:
   1. Janvier
   2. Fevrier
   ...
  11. Novembre
  12. Decembre

  Astuce: Plusieurs mois possibles avec virgule (ex: 10,11)

Entrez le(s) mois (ex: 11 ou 10,11,12): 10,11

  Astuce: Plusieurs annees possibles avec virgule (ex: 2024,2025)

Entrez l'annee(s) [2025]: 2025

Regions disponibles:
   1. auvergne-rhone-alpes
   2. bourgogne-franche-comte
   ...
   0. TOUTES les regions

Entrez les numeros des regions (ex: 1,3,5) ou 0 pour toutes: 1,3,10

----------------------------------------
  Mois:    octobre, novembre
  Annees:  2025
  Regions: auvergne-rhone-alpes, bretagne, ile-de-france
----------------------------------------

Lancer l'analyse ? (O/n): o
```

---

### Option 2 : Ligne de commande directe

```powershell
# UN mois, UNE année, TOUTES les régions
python main.py 11 2025

# PLUSIEURS mois (séparés par virgule)
python main.py 10,11,12 2025

# PLUSIEURS années (séparés par virgule)
python main.py 11 2024,2025

# PLUSIEURS mois ET années (toutes les combinaisons)
python main.py 10,11 2024,2025

# Certaines régions seulement
python main.py 11 2025 bretagne ile-de-france paca

# Forcer la ré-analyse (ignorer le cache)
python main.py 11 2025 --force
```

---

### Option 3 : Tester une seule région

```powershell
python main.py 11 2025 bretagne
```

Utile pour vérifier que tout fonctionne avant de lancer toutes les régions.

---

### Syntaxe des paramètres

| Paramètre | Format | Exemples |
|-----------|--------|----------|
| **Mois** | Numéro ou nom, virgule pour multiples | `11` ou `novembre` ou `10,11,12` |
| **Année** | AAAA, virgule pour multiples | `2025` ou `2024,2025` |
| **Régions** | Noms séparés par espaces | `bretagne paca normandie` |

---

## 📂 Où trouver les résultats

Tous les résultats sont dans :
```
C:\Users\TON_NOM\Documents\SmartARS\
```

### Structure des dossiers

```
Documents/SmartARS/
├── SmartARS_Historique.xlsx          # ← FICHIER PRINCIPAL (toutes les données)
├── SmartARS.log                       # Log global
└── results/
    └── 2025_novembre/                 # Un dossier par mois analysé
        ├── bretagne/
        │   ├── RAA_029_2025_0042_EXTRACT.pdf
        │   └── RAA_029_2025_0045_EXTRACT.pdf
        ├── ile-de-france/
        │   └── RAA_075_2025_0123_EXTRACT.pdf
        └── ...
```

### Le fichier Excel `SmartARS_Historique.xlsx`

- **Une feuille par mois** (ex: "2025_novembre", "2025_octobre")
- **Colonnes** : Region, Source (URL), Page, Equipements, Etablissement, Code_Postal
- **Pas de doublons** : les entrées existantes ne sont pas recréées

### Les PDFs extraits

Chaque PDF contient :
- **Pages 1-3** : Page de garde et sommaire du RAA original
- **Pages pertinentes** : Les pages contenant des autorisations d'équipements

Nom du fichier = nom du RAA original + `_EXTRACT.pdf`

---

## 🔍 Équipements recherchés

| Mot-clé | Description |
|---------|-------------|
| **IRM** | Imagerie par Résonance Magnétique |
| **Scanner / Scanographe** | Tomodensitométrie |
| **TEP** | Tomographie par Émission de Positons |
| **Gamma** | Caméra à scintillation |
| **Tomographe** | Appareil de tomographie |
| **Radiologie** | Équipements radiologiques |
| **Imagerie en coupes** | Modalités d'imagerie en coupes |
| **Bilan Quantitatif/Quantifié** | Documents de bilan EML |

---

## 🗺️ Régions couvertes (17)

| Région | Nom pour la commande |
|--------|---------------------|
| Auvergne-Rhône-Alpes | `auvergne-rhone-alpes` |
| Bourgogne-Franche-Comté | `bourgogne-franche-comte` |
| Bretagne | `bretagne` |
| Centre-Val de Loire | `centre-val-de-loire` |
| Corse | `corse` |
| Grand Est | `grand-est` |
| Guadeloupe | `guadeloupe` |
| Guyane | `guyane` |
| Hauts-de-France | `hauts-de-france` |
| Île-de-France | `ile-de-france` |
| Martinique | `martinique` |
| Normandie | `normandie` |
| Nouvelle-Aquitaine | `nouvelle-aquitaine` |
| Occitanie | `occitanie` |
| Pays de la Loire | `pays-de-la-loire` |
| Provence-Alpes-Côte d'Azur | `paca` ou `provence-alpes-cote-azur` |
| La Réunion | `reunion` |

---

## 🛠️ Dépannage

### "python n'est pas reconnu"
→ Python n'est pas installé ou pas dans le PATH. Réinstalle Python en cochant "Add to PATH".

### "No module named 'requests'"
→ L'environnement n'est pas activé ou les dépendances pas installées :
```powershell
.\env\Scripts\activate
pip install -r requirements.txt
```

### "0 PDF trouvé" pour une région
→ Soit il n'y a pas de RAA pour ce mois, soit le site de la préfecture a changé. Vérifier manuellement sur le site.

### Erreur de téléchargement / Timeout
→ Le script fait 3 tentatives automatiques. Si ça échoue toujours, le site est peut-être indisponible.

### Je veux relancer l'analyse d'un mois déjà fait
→ Utilise `--force` pour ignorer le cache :
```powershell
python main.py novembre 2025 --force
```

---

## ⚙️ Configuration avancée

Éditer `config.py` pour modifier :

- `KEYWORDS_REGEX` : Patterns de détection des équipements
- `KEYWORDS_AUTORISATION` : Mots confirmant une autorisation
- `TIMEOUT_PAGE` / `TIMEOUT_PDF` : Délais de téléchargement (défaut: 30s / 60s)
- `MAX_RETRIES` : Nombre de tentatives en cas d'échec (défaut: 3)

---

## 📁 Structure du code

```
SmartARS/
├── main.py              # Point d'entrée, orchestration
├── config.py            # Configuration globale
├── utils.py             # Fonctions : scraping, analyse PDF, téléchargement
├── requirements.txt     # Dépendances Python
├── README.md            # Ce fichier
└── regions/             # Un fichier par région
    ├── __init__.py
    ├── bretagne.py
    ├── ile_de_france.py
    └── ...
```

---

## 📝 Logs

Les logs détaillés sont dans :
- `C:\Users\TON_NOM\Documents\SmartARS\SmartARS.log`

Exemple de log :
```
2025-12-05 14:30:15 - INFO - === Analyse: bretagne pour novembre 2025 ===
2025-12-05 14:30:18 - INFO - bretagne: 5 PDF a analyser
2025-12-05 14:30:45 - INFO - RAA_029_2025_0042.pdf: 2 pages pertinentes
2025-12-05 14:31:02 - INFO - bretagne: 3 pages pertinentes dans 2 PDFs
```

---

## 🔧 Commandes utiles

```powershell
# Activer l'environnement
.\env\Scripts\activate

# Lancer le programme
python main.py

# Voir l'aide
python main.py --help

# Mettre à jour les dépendances
pip install -r requirements.txt --upgrade

# Désactiver l'environnement
deactivate
```

---

## 📄 Licence

Projet interne - Usage privé.

---

## 👤 Auteur

Développé pour la veille réglementaire en imagerie médicale.
