# -*- coding: utf-8 -*-
"""
SmartARS - Utilitaires
======================
Fonctions pour le scraping et l'analyse des RAA
"""

import requests
import urllib3
import time
import fitz  # PyMuPDF
import io
import re
import logging
from bs4 import BeautifulSoup
from config import HTTP_HEADERS, TIMEOUT_PAGE, TIMEOUT_PDF, KEYWORDS, KEYWORDS_REGEX, KEYWORDS_AUTORISATION, DELAY_BETWEEN_REQUESTS, MOIS_FR, MOIS_NOMS, MOIS_NOMS_URL, MAX_RETRIES

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Logger
logger = logging.getLogger("SmartARS")


def log(message, level="INFO"):
    """
    Affiche un message formaté dans la console.
    Les erreurs et warnings sont mis en évidence.
    """
    icons = {
        "INFO": "ℹ️", "SUCCESS": "✅", "ERROR": "❌", "WARNING": "⚠️",
        "FOUND": "🎉", "SEARCH": "🔍", "DOWNLOAD": "📥", "REGION": "📍",
        "START": "🚀", "END": "🏁", "PDF": "📄",
    }
    
    icon = icons.get(level, '•')
    
    # Mise en évidence des erreurs et warnings
    if level == "ERROR":
        print()
        print("!" * 60)
        print(f"{icon} ERREUR: {message}")
        print("!" * 60)
        print()
    elif level == "WARNING":
        print(f"{icon} [ATTENTION] {message}")
    else:
        print(f"{icon} {message}")


def normaliser_mois(mois):
    """
    Convertit un mois en (nom, numero).
    Accepte: "novembre", "11", 11
    """
    if isinstance(mois, int):
        return MOIS_NOMS.get(mois, ""), mois
    
    mois_str = str(mois).lower().strip()
    
    if mois_str.isdigit():
        num = int(mois_str)
        return MOIS_NOMS.get(num, ""), num
    
    mois_clean = mois_str.replace('é', 'e').replace('û', 'u').replace('è', 'e')
    num = MOIS_FR.get(mois_str, MOIS_FR.get(mois_clean, 0))
    return mois_clean, num


def get_mois_variantes(mois_num):
    """
    Retourne les deux variantes du nom de mois (avec et sans accents).
    Utile pour essayer plusieurs URLs.
    
    Returns:
        Liste de tuples [(nom_sans_accent, nom_avec_accent), ...]
        Ex pour décembre: [("decembre", "décembre"), ("Decembre", "Décembre")]
    """
    sans_accent = MOIS_NOMS.get(mois_num, "")
    avec_accent = MOIS_NOMS_URL.get(mois_num, "")
    
    return [
        sans_accent,                    # decembre
        avec_accent,                    # décembre
        sans_accent.capitalize(),       # Decembre
        avec_accent.capitalize(),       # Décembre
    ]


def get_soup_multi_urls(urls):
    """
    Essaie plusieurs URLs et retourne le premier soup valide.
    Utile quand on ne sait pas si le site utilise des accents ou non.
    
    Args:
        urls: Liste d'URLs à essayer
        
    Returns:
        (soup, url_valide) ou (None, None)
    """
    for url in urls:
        soup = get_soup(url)
        if soup:
            return soup, url
    return None, None


def telecharger_page(url, timeout=None, is_pdf=False, max_retries=None):
    """
    Télécharge une page web ou un PDF avec retry automatique.
    
    Args:
        url: URL à télécharger
        timeout: Timeout en secondes (auto si None)
        is_pdf: True si c'est un PDF (timeout plus long)
        max_retries: Nombre max de tentatives (défaut: 3)
    
    Returns:
        Response object ou None si échec
    """
    if timeout is None:
        timeout = TIMEOUT_PDF if is_pdf else TIMEOUT_PAGE
    
    if max_retries is None:
        max_retries = MAX_RETRIES
    
    last_error = None
    
    for attempt in range(1, max_retries + 1):
        try:
            # Délai entre requêtes (augmenté si retry)
            delay = DELAY_BETWEEN_REQUESTS * attempt
            time.sleep(delay)
            
            response = requests.get(
                url, 
                headers=HTTP_HEADERS, 
                timeout=timeout, 
                verify=False,
                stream=is_pdf  # Stream pour les gros fichiers
            )
            
            if response.status_code == 200:
                # Pour les PDFs, vérifier que le contenu est complet
                if is_pdf:
                    content = response.content  # Force le téléchargement complet
                    if len(content) < 1000:  # PDF trop petit = probablement une erreur
                        logger.warning(f"PDF trop petit ({len(content)} bytes): {url}")
                        continue
                return response
            
            elif response.status_code == 404:
                # 404 = pas la peine de retry
                logger.warning(f"HTTP 404 (introuvable): {url}")
                return None
            
            elif response.status_code >= 500:
                # Erreur serveur = retry
                last_error = f"HTTP {response.status_code}"
                logger.warning(f"HTTP {response.status_code} (tentative {attempt}/{max_retries}): {url}")
            
            else:
                logger.warning(f"HTTP {response.status_code}: {url}")
                return None
                
        except requests.exceptions.Timeout:
            last_error = "Timeout"
            logger.warning(f"Timeout (tentative {attempt}/{max_retries}): {url}")
            
        except requests.exceptions.ConnectionError as e:
            last_error = "Connexion"
            error_msg = str(e)
            if "IncompleteRead" in error_msg:
                logger.warning(f"Lecture incomplete (tentative {attempt}/{max_retries}): {url}")
            else:
                logger.warning(f"Erreur connexion (tentative {attempt}/{max_retries}): {url}")
            
        except requests.exceptions.ChunkedEncodingError:
            last_error = "Encoding"
            logger.warning(f"Erreur transfert (tentative {attempt}/{max_retries}): {url}")
            
        except Exception as e:
            last_error = str(e)[:50]
            logger.warning(f"Erreur {e} (tentative {attempt}/{max_retries}): {url}")
        
        # Attente exponentielle avant retry (1s, 2s, 4s...)
        if attempt < max_retries:
            wait_time = 2 ** (attempt - 1)
            time.sleep(wait_time)
    
    # Toutes les tentatives ont échoué
    logger.error(f"Echec apres {max_retries} tentatives ({last_error}): {url}")
    return None


def get_soup(url):
    """Télécharge et parse une page HTML."""
    response = telecharger_page(url)
    if response:
        return BeautifulSoup(response.text, 'html.parser')
    return None


def contient_autre_mois(texte, mois_num, annee):
    """
    Vérifie si le texte contient EXPLICITEMENT un mois DIFFÉRENT de celui recherché.
    Utilisé pour exclure les faux positifs.
    """
    texte_lower = normaliser_accents(texte.lower())
    annee_str = str(annee)
    
    # Liste des autres mois (tous sauf celui recherché)
    autres_mois = {k: v for k, v in MOIS_NOMS.items() if k != mois_num}
    
    for num, nom in autres_mois.items():
        # Vérifier si un autre mois est explicitement mentionné avec l'année
        patterns_autre = [
            rf'\d{{1,2}}\s+{nom}\s+{annee_str}',  # "05 novembre 2025"
            rf'{nom}\s+{annee_str}',               # "novembre 2025"
            rf'{nom}[\-_]{annee_str}',             # "novembre-2025"
        ]
        for pattern in patterns_autre:
            if re.search(pattern, texte_lower):
                return True
    
    return False


def normaliser_accents(texte):
    """Supprime les accents d'un texte pour faciliter la comparaison."""
    accents = {
        'é': 'e', 'è': 'e', 'ê': 'e', 'ë': 'e',
        'à': 'a', 'â': 'a', 'ä': 'a',
        'ù': 'u', 'û': 'u', 'ü': 'u',
        'î': 'i', 'ï': 'i',
        'ô': 'o', 'ö': 'o',
        'ç': 'c',
    }
    for accent, sans in accents.items():
        texte = texte.replace(accent, sans)
    return texte


def contient_mois(texte, mois_num):
    """
    Vérifie si le texte contient le mois (avec ou sans année).
    Utile pour les pages annuelles où l'année est déjà dans l'URL.
    
    Ex: "Recueil n°614 du 04 décembre" → True pour mois_num=12
    """
    texte_lower = normaliser_accents(texte.lower())
    mois_nom = MOIS_NOMS.get(mois_num, "")
    mois_str = str(mois_num).zfill(2)
    
    # Patterns pour détecter le mois
    patterns = [
        rf'\d{{1,2}}\s+{mois_nom}',           # "04 decembre"
        rf'{mois_nom}\s*:',                    # "Décembre :"
        rf'/{mois_str}/',                      # "/12/"
        rf'-{mois_str}-',                      # "-12-"
        rf'{mois_nom}\s+\d{{4}}',              # "decembre 2025"
    ]
    
    for pattern in patterns:
        if re.search(pattern, texte_lower):
            return True
    return False


def contient_date_stricte(texte, mois_num, annee, page_annuelle=False):
    """
    Vérifie STRICTEMENT si un texte contient une date du mois/année demandé.
    
    La date doit être au format:
    - "14 novembre 2025" ou "novembre 2025"
    - "14/11/2025" ou "14-11-2025"
    - Dans l'URL: "2025-11" ou "11-2025" ou "novembre-2025"
    
    IMPORTANT: 
    - Le mois et l'année doivent être ADJACENTS (pas séparés)
    - Exclut les textes qui mentionnent explicitement un AUTRE mois
    - Gère les accents (décembre = decembre)
    
    Args:
        texte: Le texte à analyser
        mois_num: Numéro du mois (1-12)
        annee: Année (ex: 2025)
        page_annuelle: Si True, accepte le mois seul sans année (pour pages annuelles)
    """
    # Normaliser le texte : minuscules + sans accents
    texte_lower = normaliser_accents(texte.lower())
    annee_str = str(annee)
    mois_nom = MOIS_NOMS.get(mois_num, "")  # déjà sans accents dans config
    mois_str = str(mois_num).zfill(2)  # "10" pour octobre
    mois_str_simple = str(mois_num)     # "10" ou "1"
    
    # Si page annuelle, on accepte le mois seul
    if page_annuelle:
        # Vérifier qu'on ne mentionne pas un AUTRE mois explicitement
        autres_mois = [v for k, v in MOIS_NOMS.items() if k != mois_num]
        for autre in autres_mois:
            if re.search(rf'\d{{1,2}}\s+{autre}', texte_lower):
                return False  # C'est un autre mois
        # Vérifier que NOTRE mois est présent
        if contient_mois(texte, mois_num):
            return True
    
    # NOUVEAU: Si le texte mentionne explicitement un AUTRE mois, rejeter
    if contient_autre_mois(texte, mois_num, annee):
        return False
    
    # Patterns STRICTS où mois et année sont adjacents
    patterns = [
        # "14 octobre 2025" ou "octobre 2025"
        rf'\d{{1,2}}\s+{mois_nom}\s+{annee_str}',
        rf'{mois_nom}\s+{annee_str}',
        
        # "14/10/2025" ou "14-10-2025" 
        rf'\d{{1,2}}[/\-]{mois_str}[/\-]{annee_str}',
        rf'\d{{1,2}}[/\-]{mois_str_simple}[/\-]{annee_str}',
        
        # "2025-10-14" ou "2025/10/14"
        rf'{annee_str}[/\-]{mois_str}[/\-]\d{{1,2}}',
        rf'{annee_str}[/\-]{mois_str_simple}[/\-]\d{{1,2}}',
        
        # Dans les URLs: "octobre-2025" ou "2025-octobre" ou "10-2025"
        rf'{mois_nom}[\-_]{annee_str}',
        rf'{annee_str}[\-_]{mois_nom}',
        rf'{mois_str}[\-_]{annee_str}',
        rf'{annee_str}[\-_]{mois_str}[\-_]',
        
        # "2025-10" en fin de chaîne ou suivi d'un non-chiffre
        rf'{annee_str}[\-_]{mois_str}(?:[^\d]|$)',
        
        # Format compact dans URL: "10102025" ou "31102025" (jour+mois+année)
        rf'\d{{2}}{mois_str}{annee_str}',
    ]
    
    for pattern in patterns:
        if re.search(pattern, texte_lower):
            return True
    
    return False


def analyser_pdf_pages(pdf_bytes):
    """
    Analyse un PDF et retourne les pages contenant des autorisations d'équipements.
    Utilise des regex pour une détection précise.
    """
    pages_pertinentes = []
    
    # Compiler les regex une seule fois
    compiled_patterns = []
    for pattern_str in KEYWORDS_REGEX:
        try:
            compiled_patterns.append((pattern_str, re.compile(pattern_str, re.IGNORECASE)))
        except re.error:
            logger.warning(f"Regex invalide: {pattern_str}")
    
    try:
        with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:
            for page_num, page in enumerate(doc):
                text = page.get_text()
                
                # 1. Chercher les mots-clés d'équipement avec regex
                equipements_trouves = []
                for pattern_str, pattern in compiled_patterns:
                    if pattern.search(text):
                        # Extraire un nom lisible du pattern
                        nom = pattern_str.replace(r'\b', '').replace(r'\s+', ' ').replace(r'\s{1,2}', ' ')
                        nom = nom.replace('(?:s)?', '').replace('(?:s)', '')
                        nom = nom.strip()
                        if nom not in equipements_trouves:
                            equipements_trouves.append(nom)
                
                if not equipements_trouves:
                    continue
                
                # 2. Vérifier si c'est une autorisation (pas juste une mention)
                text_lower = text.lower()
                est_autorisation = any(
                    kw.lower() in text_lower 
                    for kw in KEYWORDS_AUTORISATION
                )
                
                # 3. Extraire les infos
                info = extraire_infos_page(text, equipements_trouves)
                
                pages_pertinentes.append({
                    "page_num": page_num,
                    "equipements": equipements_trouves,
                    "texte": text,
                    "est_autorisation": est_autorisation,
                    "etablissement": info.get("etablissement", ""),
                    "ville": info.get("ville", ""),
                })
                
    except Exception as e:
        logger.error(f"Erreur lecture PDF: {e}")
    
    return pages_pertinentes


def extraire_infos_page(text, equipements):
    """Extrait établissement et ville d'une page."""
    info = {"etablissement": "", "ville": ""}
    text_lower = text.lower()
    
    # Patterns pour établissement
    patterns_etab = [
        r"(?:centre hospitalier|ch |chu |chru |clinique|hôpital|hopital)[^,\n]{3,60}",
        r"(?:groupe hospitalier|ghm |gh )[^,\n]{3,60}",
        r"(?:établissement|etablissement)[^:]*:\s*([^\n,]{5,60})",
    ]
    
    for pattern in patterns_etab:
        match = re.search(pattern, text_lower)
        if match:
            info["etablissement"] = match.group(0).strip().title()[:60]
            break
    
    # Patterns pour ville (code postal)
    match_cp = re.search(r'\(?\s*(\d{5})\s*\)?', text)
    if match_cp:
        info["ville"] = match_cp.group(1)
    
    return info


def creer_pdf_synthese(pages_data, nom_fichier):
    """Crée un PDF avec les pages d'autorisations extraites."""
    if not pages_data:
        return False
    
    doc = fitz.open()
    
    # Page de garde
    page_garde = doc.new_page(width=595, height=842)
    page_garde.insert_text((50, 60), "SmartARS - Autorisations", fontsize=22, color=(0.1, 0.3, 0.6))
    page_garde.insert_text((50, 85), f"{len(pages_data)} autorisation(s) trouvée(s)", fontsize=12, color=(0.4, 0.4, 0.4))
    page_garde.draw_line((50, 100), (545, 100), color=(0.1, 0.3, 0.6), width=1)
    
    y = 130
    for i, data in enumerate(pages_data, 1):
        texte = f"{i}. [{data.get('region', '?')}] {', '.join(data.get('equipements', []))}"
        if data.get('etablissement'):
            texte += f" - {data['etablissement'][:40]}"
        
        page_garde.insert_text((50, y), texte[:90], fontsize=9, color=(0, 0, 0))
        y += 15
        
        if y > 800:
            page_garde = doc.new_page(width=595, height=842)
            y = 50
    
    # Ajouter les pages
    for data in pages_data:
        try:
            src = fitz.open(stream=data["pdf_bytes"], filetype="pdf")
            doc.insert_pdf(src, from_page=data["page_num"], to_page=data["page_num"])
            src.close()
        except:
            pass
    
    doc.save(nom_fichier)
    doc.close()
    return True
