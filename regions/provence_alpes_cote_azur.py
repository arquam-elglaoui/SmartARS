# -*- coding: utf-8 -*-
"""
Extracteur: Provence-Alpes-Côte d'Azur (PACA)
=============================================
Page annuelle avec filtrage STRICT par mois/année.
CORRIGÉ: Ne pas utiliser parent_text qui cause des faux positifs.
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import get_soup, contient_date_stricte, log

BASE_URL = "https://www.prefectures-regions.gouv.fr"


def extraire_provence_alpes_cote_azur(mois_num, annee):
    log(f"PACA - {mois_num:02d}/{annee}", "SEARCH")
    
    # Exception pour 2022 (erreur dans l'URL officielle)
    if annee == 2022:
        url = f"{BASE_URL}/provence-alpes-cote-dazur/Documents-publications/RAA-{annee}-le-Recueil-des-Actes-Administratifs-{annee}2"
    else:
        url = f"{BASE_URL}/provence-alpes-cote-dazur/Documents-publications/RAA-{annee}-le-Recueil-des-Actes-Administratifs-{annee}"
    
    soup = get_soup(url)
    if not soup:
        return []
    
    pdf_links = []
    
    for a in soup.find_all('a', href=True):
        href = a['href']
        if '.pdf' not in href.lower():
            continue
        
        text = a.get_text(strip=True)
        
        # Filtrage STRICT: uniquement texte du lien ET URL
        # page_annuelle=True car les noms de fichiers n'ont pas toujours l'année
        if contient_date_stricte(text, mois_num, annee, page_annuelle=True) or contient_date_stricte(href, mois_num, annee):
            if href.startswith('/'):
                href = BASE_URL + href
            if href not in pdf_links:
                pdf_links.append(href)
                log(f"  {text[:55]}...", "PDF")
    
    log(f"  → {len(pdf_links)} PDF", "SUCCESS" if pdf_links else "WARNING")
    return pdf_links
