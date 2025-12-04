# -*- coding: utf-8 -*-
"""
SmartARS - Configuration
========================
"""

# === MOTS-CLÉS À RECHERCHER DANS LES PDF (REGEX) ===
# Ces patterns sont utilisés pour détecter les autorisations d'équipements lourds
# \b = limite de mot (évite les faux positifs comme "IRMATION")
# (?:s)? = gère singulier/pluriel
# \s{1,2} = 1 ou 2 espaces (gère espaces insécables)
KEYWORDS_REGEX = [
    r'Bilan(?:s)?\s+Quantitatif(?:s)?',
    r'Bilan(?:s)?\s+Quantifié(?:s)?',
    r'\bTEP\b',
    r'\bIRM\b',
    r'Résonance\s+Magnétique',
    r'Scanographe',
    r'\bScanner\b',
    r'Tomographe',
    r'Scintillation',
    r'\bGamma\b',
    r'Radiologie',
    r'imagerie\s{1,2}en\s{1,2}coupes',
    r'imagerie\s+médicale',
    r'équipement(?:s)?\s+lourd(?:s)?',
]

# Version simple pour affichage
KEYWORDS = [
    "IRM", "Scanner", "TEP", "Radiologie", "Tomographe", 
    "Scintillation", "Gamma", "Résonance Magnétique",
    "imagerie médicale", "imagerie en coupes", "équipement lourd",
    "Bilan Quantitatif", "Bilan Quantifié", "Scanographe",
]

# === MOTS-CLÉS D'AUTORISATION (pour filtrer les vraies autorisations) ===
KEYWORDS_AUTORISATION = [
    "autorisation",
    "autorise",
    "autorisé",
    "arrêté",
    "décision",
    "agrément",
    "l.6122",
    "l6122",
]

# === MAPPING MOIS ===
MOIS_FR = {
    "janvier": 1, "fevrier": 2, "février": 2, "mars": 3, "avril": 4,
    "mai": 5, "juin": 6, "juillet": 7, "aout": 8, "août": 8,
    "septembre": 9, "octobre": 10, "novembre": 11, "decembre": 12, "décembre": 12,
}

MOIS_NOMS = {
    1: "janvier", 2: "fevrier", 3: "mars", 4: "avril", 5: "mai", 6: "juin",
    7: "juillet", 8: "aout", 9: "septembre", 10: "octobre", 11: "novembre", 12: "decembre",
}

# === HEADERS HTTP ===
HTTP_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
}

# === TIMEOUTS ET RETRY ===
TIMEOUT_PAGE = 30          # Timeout pour les pages HTML (secondes)
TIMEOUT_PDF = 120          # Timeout pour les PDF (secondes)
DELAY_BETWEEN_REQUESTS = 0.5  # Délai entre requêtes (secondes)
MAX_RETRIES = 3            # Nombre de tentatives en cas d'échec
